"""Friends: search, requests, accept/decline, unfriend."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select

from app.core.scoring import league_for_rating
from app.dependencies import CurrentUser, DbSession
from app.models import FriendRequest, UserData
from app.schemas import DuelOpponent, FriendRequestRead, UserSummary

router = APIRouter(prefix="/friends", tags=["friends"])


def _opponent(user: UserData) -> DuelOpponent:
    return DuelOpponent(user_id=user.id, username=user.username, name=user.name, rating=user.user_rating, league=league_for_rating(user.user_rating))


async def _friend_ids(db: DbSession, user_id: int) -> set[int]:
    rows = await db.scalars(
        select(FriendRequest).where(
            FriendRequest.status == "accepted",
            or_(FriendRequest.requester_id == user_id, FriendRequest.addressee_id == user_id),
        )
    )
    return {r.addressee_id if r.requester_id == user_id else r.requester_id for r in rows}


@router.get("/search", response_model=list[UserSummary])
async def search_users(current_user: CurrentUser, db: DbSession, q: str = Query(min_length=1, max_length=60)) -> list[UserSummary]:
    users = list(
        (
            await db.scalars(
                select(UserData)
                .where(UserData.username.ilike(f"%{q}%"), UserData.id != current_user.id, UserData.is_active.is_(True))
                .order_by(UserData.username)
                .limit(20)
            )
        ).all()
    )
    if not users:
        return []
    friend_ids = await _friend_ids(db, current_user.id)
    pending = list(
        (
            await db.scalars(
                select(FriendRequest).where(
                    FriendRequest.status == "pending",
                    or_(
                        FriendRequest.requester_id == current_user.id,
                        FriendRequest.addressee_id == current_user.id,
                    ),
                )
            )
        ).all()
    )
    outgoing = {r.addressee_id for r in pending if r.requester_id == current_user.id}
    incoming = {r.requester_id for r in pending if r.addressee_id == current_user.id}

    results: list[UserSummary] = []
    for user in users:
        status_label = "none"
        if user.id in friend_ids:
            status_label = "friends"
        elif user.id in outgoing:
            status_label = "pending_outgoing"
        elif user.id in incoming:
            status_label = "pending_incoming"
        results.append(
            UserSummary(
                user_id=user.id,
                username=user.username,
                name=user.name,
                college_name=user.college_name,
                rating=user.user_rating,
                league=league_for_rating(user.user_rating),
                friend_status=status_label,
            )
        )
    return results


@router.get("", response_model=list[UserSummary])
async def list_friends(current_user: CurrentUser, db: DbSession) -> list[UserSummary]:
    friend_ids = await _friend_ids(db, current_user.id)
    if not friend_ids:
        return []
    users = list((await db.scalars(select(UserData).where(UserData.id.in_(friend_ids)).order_by(UserData.name))).all())
    return [
        UserSummary(
            user_id=u.id, username=u.username, name=u.name, college_name=u.college_name,
            rating=u.user_rating, league=league_for_rating(u.user_rating), friend_status="friends",
        )
        for u in users
    ]


@router.get("/requests", response_model=list[FriendRequestRead])
async def list_incoming_requests(current_user: CurrentUser, db: DbSession) -> list[FriendRequestRead]:
    rows = list(
        (
            await db.scalars(
                select(FriendRequest).where(FriendRequest.addressee_id == current_user.id, FriendRequest.status == "pending").order_by(FriendRequest.created_at.desc())
            )
        ).all()
    )
    if not rows:
        return []
    user_ids = {r.requester_id for r in rows} | {current_user.id}
    users = {u.id: u for u in (await db.scalars(select(UserData).where(UserData.id.in_(user_ids)))).all()}
    return [
        FriendRequestRead(id=r.id, status=r.status, requester=_opponent(users[r.requester_id]), addressee=_opponent(users[current_user.id]), created_at=r.created_at)
        for r in rows
        if r.requester_id in users
    ]


@router.post("/requests/{username}", response_model=FriendRequestRead, status_code=status.HTTP_201_CREATED)
async def send_friend_request(username: str, current_user: CurrentUser, db: DbSession) -> FriendRequestRead:
    if username.lower() == current_user.username.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't friend yourself")
    target = await db.scalar(select(UserData).where(UserData.username.ilike(username), UserData.is_active.is_(True)))
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with that username")

    existing = await db.scalar(
        select(FriendRequest).where(
            or_(
                (FriendRequest.requester_id == current_user.id) & (FriendRequest.addressee_id == target.id),
                (FriendRequest.requester_id == target.id) & (FriendRequest.addressee_id == current_user.id),
            )
        )
    )
    if existing is not None:
        if existing.status == "accepted":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You're already friends")
        if existing.status == "pending":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A friend request is already pending")
        existing.status = "pending"
        existing.requester_id = current_user.id
        existing.addressee_id = target.id
        existing.responded_at = None
        request = existing
    else:
        request = FriendRequest(requester_id=current_user.id, addressee_id=target.id, status="pending")
        db.add(request)
    await db.commit()
    await db.refresh(request)
    return FriendRequestRead(id=request.id, status=request.status, requester=_opponent(current_user), addressee=_opponent(target), created_at=request.created_at)


async def _get_incoming_request(db: DbSession, request_id: int, current_user: UserData) -> FriendRequest:
    request = await db.get(FriendRequest, request_id)
    if request is None or request.addressee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend request not found")
    if request.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This request was already handled")
    return request


@router.post("/requests/{request_id}/accept", response_model=FriendRequestRead)
async def accept_friend_request(request_id: int, current_user: CurrentUser, db: DbSession) -> FriendRequestRead:
    request = await _get_incoming_request(db, request_id, current_user)
    request.status = "accepted"
    request.responded_at = datetime.now(UTC)
    requester = await db.get(UserData, request.requester_id)
    await db.commit()
    return FriendRequestRead(id=request.id, status=request.status, requester=_opponent(requester), addressee=_opponent(current_user), created_at=request.created_at)


@router.post("/requests/{request_id}/decline", status_code=status.HTTP_204_NO_CONTENT)
async def decline_friend_request(request_id: int, current_user: CurrentUser, db: DbSession) -> None:
    request = await _get_incoming_request(db, request_id, current_user)
    request.status = "declined"
    request.responded_at = datetime.now(UTC)
    await db.commit()


@router.delete("/{friend_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(friend_user_id: int, current_user: CurrentUser, db: DbSession) -> None:
    request = await db.scalar(
        select(FriendRequest).where(
            FriendRequest.status == "accepted",
            or_(
                (FriendRequest.requester_id == current_user.id) & (FriendRequest.addressee_id == friend_user_id),
                (FriendRequest.requester_id == friend_user_id) & (FriendRequest.addressee_id == current_user.id),
            ),
        )
    )
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You're not friends with this user")
    await db.delete(request)
    await db.commit()

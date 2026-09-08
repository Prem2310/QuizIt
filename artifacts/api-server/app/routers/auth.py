from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import or_, select

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.core.serializers import to_user_read
from app.dependencies import CurrentUser, DbSession
from app.models import UserData
from app.schemas import AuthResponse, UserCreate, UserLogin, UserRead, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])


def set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure=settings.cookie_secure,
        # Frontend and API live on different domains in production (Netlify + Render/etc.),
        # so the cookie must be SameSite=None to be sent on those cross-site requests.
        # Browsers only accept SameSite=None alongside Secure, hence the pairing with
        # cookie_secure. Local dev stays "lax" since it's same-site http://localhost.
        samesite="none" if settings.cookie_secure else "lax",
        max_age=settings.access_token_expire_minutes * 60,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, response: Response, db: DbSession) -> AuthResponse:
    existing = await db.scalar(select(UserData).where(or_(UserData.email == payload.email, UserData.username == payload.username)))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username is already registered")
    user = UserData(
        name=payload.name,
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        college_name=payload.college_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return AuthResponse(access_token=token, user=to_user_read(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLogin, response: Response, db: DbSession) -> AuthResponse:
    user = await db.scalar(select(UserData).where(or_(UserData.email == payload.email_or_username, UserData.username == payload.email_or_username)))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.id)
    set_auth_cookie(response, token)
    return AuthResponse(access_token=token, user=to_user_read(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        "access_token",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="none" if settings.cookie_secure else "lax",
    )


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser) -> UserRead:
    return to_user_read(current_user)


@router.patch("/me", response_model=UserRead)
async def update_me(payload: UserUpdate, current_user: CurrentUser, db: DbSession) -> UserRead:
    if payload.username and payload.username != current_user.username:
        taken = await db.scalar(select(UserData).where(UserData.username == payload.username, UserData.id != current_user.id))
        if taken:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already in use")
        current_user.username = payload.username
    if payload.name is not None:
        current_user.name = payload.name
    if payload.college_name is not None:
        current_user.college_name = payload.college_name
    if payload.profile_picture_url is not None:
        current_user.profile_picture_url = payload.profile_picture_url
    await db.commit()
    await db.refresh(current_user)
    return to_user_read(current_user)

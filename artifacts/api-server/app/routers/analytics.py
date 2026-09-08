from collections import defaultdict
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Query
from sqlalchemy import Integer, desc, func, or_, select

from app.core.scoring import league_for_rating
from app.dependencies import CurrentUser, DbSession
from app.models import FriendRequest, Question, QuizHistory, Subtopic, Topic, UserData, UserQuestionStats, UserQuizHistory, UserQuizResponse
from app.schemas import AnalyticsSummary, AttemptSummary, LeaderboardEntry, LeaderboardScope, ProgressTrendPoint, TopicInsight

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/me", response_model=AnalyticsSummary)
async def my_summary(current_user: CurrentUser, db: DbSession) -> AnalyticsSummary:
    total = current_user.total_correct + current_user.total_incorrect
    accuracy = round(current_user.total_correct / total * 100, 2) if total else 0
    weak_topic = await db.scalar(
        select(Topic.name)
        .join(Subtopic, Subtopic.topic_id == Topic.id)
        .join(Question, Question.subtopic_id == Subtopic.id)
        .join(UserQuizResponse, UserQuizResponse.question_id == Question.id)
        .join(UserQuizHistory, UserQuizHistory.id == UserQuizResponse.user_quiz_history_id)
        .where(UserQuizHistory.user_id == current_user.id, UserQuizResponse.is_correct.is_(False))
        .group_by(Topic.id, Topic.name)
        .order_by(desc(func.count(UserQuizResponse.id)))
        .limit(1)
    )
    topic = weak_topic or await db.scalar(select(Topic.name).where(Topic.is_active.is_(True)).order_by(Topic.name).limit(1))
    due_for_review = await db.scalar(
        select(func.count(UserQuestionStats.id)).where(UserQuestionStats.user_id == current_user.id, UserQuestionStats.due_at <= func.now())
    )
    rank = await db.scalar(select(func.count(UserData.id)).where(UserData.is_active.is_(True), UserData.user_rating > current_user.user_rating))
    return AnalyticsSummary(
        total_points=current_user.total_points,
        total_correct=current_user.total_correct,
        total_incorrect=current_user.total_incorrect,
        accuracy=accuracy,
        matches_played=current_user.matches_played,
        rating=current_user.user_rating,
        rank=int(rank or 0) + 1,
        recommended_topic=topic,
        current_streak=current_user.current_streak,
        max_streak=current_user.max_streak,
        total_xp=current_user.total_xp,
        league=league_for_rating(current_user.user_rating),
        due_for_review=int(due_for_review or 0),
    )


def _entry(user: UserData, rank: int, is_me: bool) -> LeaderboardEntry:
    return LeaderboardEntry(
        rank=rank,
        user_id=user.id,
        username=user.username,
        name=user.name,
        college_name=user.college_name,
        total_points=user.total_points,
        user_rating=user.user_rating,
        league=league_for_rating(user.user_rating),
        is_me=is_me,
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def leaderboard(
    db: DbSession,
    current_user: CurrentUser,
    scope: LeaderboardScope = Query(default="global"),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[LeaderboardEntry]:
    query = select(UserData).where(UserData.is_active.is_(True))
    if scope == "college":
        if not current_user.college_name:
            return []
        query = query.where(UserData.college_name == current_user.college_name)
    elif scope == "friends":
        friend_rows = list(
            (
                await db.scalars(
                    select(FriendRequest).where(
                        FriendRequest.status == "accepted",
                        or_(FriendRequest.requester_id == current_user.id, FriendRequest.addressee_id == current_user.id),
                    )
                )
            ).all()
        )
        friend_ids = {r.addressee_id if r.requester_id == current_user.id else r.requester_id for r in friend_rows}
        friend_ids.add(current_user.id)
        if len(friend_ids) <= 1:
            return []
        query = query.where(UserData.id.in_(friend_ids))

    query = query.order_by(desc(UserData.user_rating), desc(UserData.total_points), UserData.username).limit(limit)
    users = list((await db.scalars(query)).all())
    entries = [_entry(user, rank, user.id == current_user.id) for rank, user in enumerate(users, start=1)]

    # Always surface the signed-in user's own standing, even outside the top N.
    if not any(e.is_me for e in entries) and scope != "friends":
        base_query = select(func.count(UserData.id)).where(UserData.is_active.is_(True), UserData.user_rating > current_user.user_rating)
        if scope == "college":
            base_query = base_query.where(UserData.college_name == current_user.college_name)
        my_rank = int((await db.scalar(base_query)) or 0) + 1
        entries.append(_entry(current_user, my_rank, True))

    return entries


@router.get("/me/history", response_model=list[AttemptSummary])
async def my_history(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    topic_id: int | None = Query(default=None),
    mode: str | None = Query(default=None),
) -> list[AttemptSummary]:
    query = select(UserQuizHistory).where(UserQuizHistory.user_id == current_user.id, UserQuizHistory.status == "completed")
    if topic_id is not None or mode is not None:
        query = query.join(QuizHistory, QuizHistory.id == UserQuizHistory.quiz_history_id)
        if topic_id is not None:
            query = query.where(QuizHistory.topic_id == topic_id)
        if mode is not None:
            query = query.where(QuizHistory.quiz_mode == mode)
    query = query.order_by(desc(UserQuizHistory.started_at)).limit(limit)
    attempts = list((await db.scalars(query)).all())

    quiz_ids = {attempt.quiz_history_id for attempt in attempts}
    quizzes = {
        quiz.id: quiz
        for quiz in (await db.scalars(select(QuizHistory).where(QuizHistory.id.in_(quiz_ids)))).all()
    } if quiz_ids else {}
    return [
        AttemptSummary(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_history_id,
            quiz_mode=quizzes[attempt.quiz_history_id].quiz_mode,
            score=attempt.points_scored,
            total_correct=attempt.correct_count,
            total_incorrect=attempt.incorrect_count,
            accuracy=round(attempt.correct_count / (attempt.correct_count + attempt.incorrect_count) * 100, 2)
            if attempt.correct_count + attempt.incorrect_count
            else 0,
            completed_at=attempt.completed_at,
        )
        for attempt in attempts
        if attempt.quiz_history_id in quizzes
    ]


@router.get("/me/topics", response_model=list[TopicInsight])
async def my_topic_insights(current_user: CurrentUser, db: DbSession, days: int | None = Query(default=None, ge=1, le=365)) -> list[TopicInsight]:
    query = (
        select(
            Topic.id,
            Topic.name,
            func.count(UserQuizResponse.id),
            func.sum(func.cast(UserQuizResponse.is_correct, Integer)),
        )
        .join(Subtopic, Subtopic.topic_id == Topic.id)
        .join(Question, Question.subtopic_id == Subtopic.id)
        .join(UserQuizResponse, UserQuizResponse.question_id == Question.id)
        .join(UserQuizHistory, UserQuizHistory.id == UserQuizResponse.user_quiz_history_id)
        .where(UserQuizHistory.user_id == current_user.id)
    )
    if days is not None:
        since = datetime.now(UTC) - timedelta(days=days)
        query = query.where(UserQuizResponse.created_at >= since)
    query = query.group_by(Topic.id, Topic.name).order_by(desc(func.count(UserQuizResponse.id)))
    rows = (await db.execute(query)).all()
    return [
        TopicInsight(
            topic_id=topic_id,
            topic_name=topic_name,
            total_answered=int(total_answered or 0),
            correct=int(correct or 0),
            accuracy=round(int(correct or 0) / int(total_answered) * 100, 2) if total_answered else 0,
        )
        for topic_id, topic_name, total_answered, correct in rows
    ]


@router.get("/me/trend", response_model=list[ProgressTrendPoint])
async def my_progress_trend(current_user: CurrentUser, db: DbSession, days: int = Query(default=30, ge=7, le=180)) -> list[ProgressTrendPoint]:
    """Daily accuracy trend for the progress chart, bucketed in Python so it works on both SQLite and Postgres."""
    since = datetime.now(UTC) - timedelta(days=days)
    rows = list(
        (
            await db.scalars(
                select(UserQuizResponse)
                .join(UserQuizHistory, UserQuizHistory.id == UserQuizResponse.user_quiz_history_id)
                .where(UserQuizHistory.user_id == current_user.id, UserQuizResponse.created_at >= since)
            )
        ).all()
    )
    buckets: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # date -> [correct, incorrect]
    for row in rows:
        key = row.created_at.date().isoformat()
        buckets[key][0 if row.is_correct else 1] += 1

    points = []
    for key in sorted(buckets):
        correct, incorrect = buckets[key]
        attempts = correct + incorrect
        points.append(
            ProgressTrendPoint(
                date=key,
                attempts=attempts,
                correct=correct,
                incorrect=incorrect,
                accuracy=round(correct / attempts * 100, 2) if attempts else 0,
            )
        )
    return points

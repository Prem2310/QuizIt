"""Create the QuizIt core tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001_quizit_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("topic",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("slug", sa.String(140), nullable=False, unique=True),
    )
    op.create_table("subtopic",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topic.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("slug", sa.String(140), nullable=False),
    )
    op.create_table("user_data",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("username", sa.String(40), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("college_name", sa.String(180)),
        sa.Column("profile_picture_url", sa.String(500)),
        sa.Column("date_joined", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("total_points", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_correct", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_incorrect", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rank", sa.Integer()),
        sa.Column("user_rating", sa.Float(), server_default="1000", nullable=False),
        sa.Column("matches_played", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table("question",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subtopic_id", sa.Integer(), sa.ForeignKey("subtopic.id"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("text_html", sa.Text()),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("options_html", sa.JSON()),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("answer_letter", sa.String(4)),
        sa.Column("explanation", sa.Text()),
        sa.Column("explanation_html", sa.Text()),
        sa.Column("difficulty", sa.String(20), server_default="medium", nullable=False),
        sa.Column("page", sa.Integer()),
        sa.Column("source", sa.String(255)),
        sa.Column("source_url", sa.String(500)),
        sa.Column("question_hash", sa.String(128), unique=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table("quiz_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("room_id", sa.String(80)),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topic.id")),
        sa.Column("time_per_question", sa.Integer(), server_default="30", nullable=False),
        sa.Column("num_questions", sa.Integer(), nullable=False),
        sa.Column("quiz_mode", sa.String(30), server_default="practice", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table("quiz_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("quiz_history_id", sa.Integer(), sa.ForeignKey("quiz_history.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("question.id"), nullable=False),
        sa.Column("question_order", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table("user_quiz_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user_data.id"), nullable=False),
        sa.Column("quiz_history_id", sa.Integer(), sa.ForeignKey("quiz_history.id"), nullable=False),
        sa.Column("score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_correct", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_incorrect", sa.Integer(), server_default="0", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_table("user_quiz_response",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_quiz_history_id", sa.Integer(), sa.ForeignKey("user_quiz_history.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("question.id"), nullable=False),
        sa.Column("selected_answer", sa.Text()),
        sa.Column("is_correct", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("time_taken", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    for table in ("user_quiz_response", "user_quiz_history", "quiz_questions", "quiz_history", "question", "user_data", "subtopic", "topic"):
        op.drop_table(table)
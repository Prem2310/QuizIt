"""Add duel/mastery features and align schema with the real IndiaBix dataset.

Pre-launch schema rework: no real users/attempts exist yet against Postgres, so the
affected tables (question, quiz_questions, user_quiz_history, user_quiz_response) are
dropped and recreated rather than incrementally altered. `question.id` moves from an
Integer surrogate key to the String id used by the scraped dataset
(e.g. ``aptitude_alligation-or-mixture_1_0``).

Note:
    `0002_matiks_features` already adds:
    - current_streak
    - max_streak
    - last_active_date
    - speed_wpm
    - preferred_mode

This migration therefore only adds the new:
    - total_xp
    - best_rating
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_duel_and_mastery"
down_revision = "0002_matiks_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # Rebuild question-related tables to match the IndiaBix dataset structure.
    # -------------------------------------------------------------------------

    op.drop_table("user_quiz_response")
    op.drop_table("quiz_questions")
    op.drop_table("user_quiz_history")
    op.drop_table("question")

    op.create_table(
        "question",
        sa.Column("id", sa.String(160), primary_key=True),
        sa.Column(
            "subtopic_id",
            sa.Integer(),
            sa.ForeignKey("subtopic.id"),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("text_html", sa.Text()),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("options_html", sa.JSON()),
        sa.Column("answer", sa.Text()),
        sa.Column("answer_letter", sa.String(4)),
        sa.Column("explanation", sa.Text()),
        sa.Column("explanation_html", sa.Text()),
        sa.Column("difficulty", sa.String(20), server_default="medium"),
        sa.Column("page", sa.Integer()),
        sa.Column(
            "source",
            sa.String(255),
            server_default="indiabix",
            nullable=False,
        ),
        sa.Column("source_url", sa.String(500)),
        sa.Column("question_hash", sa.String(160), unique=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "quiz_history_id",
            sa.Integer(),
            sa.ForeignKey("quiz_history.id"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            sa.String(160),
            sa.ForeignKey("question.id"),
            nullable=False,
        ),
        sa.Column(
            "question_order",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "marks",
            sa.Numeric(),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "negative_marks",
            sa.Numeric(),
            server_default="0",
            nullable=False,
        ),
    )

    op.create_table(
        "user_quiz_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user_data.id"),
            nullable=False,
        ),
        sa.Column(
            "quiz_history_id",
            sa.Integer(),
            sa.ForeignKey("quiz_history.id"),
            nullable=False,
        ),
        sa.Column(
            "points_scored",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "correct_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "incorrect_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "skipped_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("time_taken_seconds", sa.Integer()),
        sa.Column(
            "status",
            sa.String(20),
            server_default="in_progress",
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "user_quiz_response",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_quiz_history_id",
            sa.Integer(),
            sa.ForeignKey("user_quiz_history.id"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            sa.String(160),
            sa.ForeignKey("question.id"),
            nullable=False,
        ),
        sa.Column("attempted_option", sa.String(4)),
        sa.Column("selected_answer", sa.Text()),
        sa.Column(
            "is_correct",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "marks_obtained",
            sa.Numeric(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("start_time", sa.DateTime(timezone=True)),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column("time_taken_seconds", sa.Integer()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # -------------------------------------------------------------------------
    # Update quiz_history schema.
    # -------------------------------------------------------------------------

    op.alter_column(
        "quiz_history",
        "time_per_question",
        existing_type=sa.Integer(),
        nullable=True,
        server_default=None,
    )

    op.alter_column(
        "quiz_history",
        "num_questions",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.create_unique_constraint(
        "uq_quiz_history_room_id",
        "quiz_history",
        ["room_id"],
    )

    # -------------------------------------------------------------------------
    # Add ONLY the new user_data columns.
    #
    # current_streak, max_streak, last_active_date and preferred_mode
    # were already created by 0002_matiks_features.
    # -------------------------------------------------------------------------

    op.add_column(
        "user_data",
        sa.Column(
            "total_xp",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )

    op.add_column(
        "user_data",
        sa.Column(
            "best_rating",
            sa.Float(),
            server_default="1000",
            nullable=False,
        ),
    )

    # -------------------------------------------------------------------------
    # User question mastery / spaced repetition statistics.
    # -------------------------------------------------------------------------

    op.create_table(
        "user_question_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user_data.id"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            sa.String(160),
            sa.ForeignKey("question.id"),
            nullable=False,
        ),
        sa.Column(
            "subtopic_id",
            sa.Integer(),
            sa.ForeignKey("subtopic.id"),
            nullable=False,
        ),
        sa.Column(
            "box_level",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "times_seen",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "times_correct",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "times_incorrect",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column(
            "due_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "user_id",
            "question_id",
            name="uq_user_question_stats_user_question",
        ),
    )

    op.create_index(
        "ix_user_question_stats_user_id",
        "user_question_stats",
        ["user_id"],
    )

    op.create_index(
        "ix_user_question_stats_question_id",
        "user_question_stats",
        ["question_id"],
    )

    op.create_index(
        "ix_user_question_stats_subtopic_id",
        "user_question_stats",
        ["subtopic_id"],
    )

    op.create_index(
        "ix_user_question_stats_due_at",
        "user_question_stats",
        ["due_at"],
    )

    # -------------------------------------------------------------------------
    # Duel match table.
    # -------------------------------------------------------------------------

    op.create_table(
        "duel_match",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "quiz_history_id",
            sa.Integer(),
            sa.ForeignKey("quiz_history.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "topic_id",
            sa.Integer(),
            sa.ForeignKey("topic.id"),
        ),
        sa.Column(
            "player1_id",
            sa.Integer(),
            sa.ForeignKey("user_data.id"),
            nullable=False,
        ),
        sa.Column(
            "player2_id",
            sa.Integer(),
            sa.ForeignKey("user_data.id"),
            nullable=False,
        ),
        sa.Column(
            "player1_attempt_id",
            sa.Integer(),
            sa.ForeignKey("user_quiz_history.id"),
        ),
        sa.Column(
            "player2_attempt_id",
            sa.Integer(),
            sa.ForeignKey("user_quiz_history.id"),
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="waiting",
            nullable=False,
        ),
        sa.Column(
            "player1_rating_before",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "player2_rating_before",
            sa.Float(),
            nullable=False,
        ),
        sa.Column("player1_rating_after", sa.Float()),
        sa.Column("player2_rating_after", sa.Float()),
        sa.Column(
            "winner_id",
            sa.Integer(),
            sa.ForeignKey("user_data.id"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    op.create_index(
        "ix_duel_match_player1_id",
        "duel_match",
        ["player1_id"],
    )

    op.create_index(
        "ix_duel_match_player2_id",
        "duel_match",
        ["player2_id"],
    )


def downgrade() -> None:
    # -------------------------------------------------------------------------
    # Remove duel/mastery tables.
    # -------------------------------------------------------------------------

    op.drop_table("duel_match")
    op.drop_table("user_question_stats")

    # -------------------------------------------------------------------------
    # Remove ONLY the columns introduced by this migration.
    #
    # current_streak, max_streak, last_active_date and preferred_mode
    # belong to 0002_matiks_features and must remain.
    # -------------------------------------------------------------------------

    op.drop_column("user_data", "best_rating")
    op.drop_column("user_data", "total_xp")

    # -------------------------------------------------------------------------
    # Revert quiz_history changes.
    # -------------------------------------------------------------------------

    op.drop_constraint(
        "uq_quiz_history_room_id",
        "quiz_history",
        type_="unique",
    )

    op.alter_column(
        "quiz_history",
        "num_questions",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "quiz_history",
        "time_per_question",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="30",
    )

    # -------------------------------------------------------------------------
    # Restore the previous question-related schema.
    # -------------------------------------------------------------------------

    op.drop_table("user_quiz_response")
    op.drop_table("user_quiz_history")
    op.drop_table("quiz_questions")
    op.drop_table("question")

    op.create_table(
        "question",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "subtopic_id",
            sa.Integer(),
            sa.ForeignKey("subtopic.id"),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("text_html", sa.Text()),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("options_html", sa.JSON()),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("answer_letter", sa.String(4)),
        sa.Column("explanation", sa.Text()),
        sa.Column("explanation_html", sa.Text()),
        sa.Column(
            "difficulty",
            sa.String(20),
            server_default="medium",
            nullable=False,
        ),
        sa.Column("page", sa.Integer()),
        sa.Column("source", sa.String(255)),
        sa.Column("source_url", sa.String(500)),
        sa.Column("question_hash", sa.String(128), unique=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "quiz_history_id",
            sa.Integer(),
            sa.ForeignKey("quiz_history.id"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            sa.Integer(),
            sa.ForeignKey("question.id"),
            nullable=False,
        ),
        sa.Column(
            "question_order",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )

    op.create_table(
        "user_quiz_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user_data.id"),
            nullable=False,
        ),
        sa.Column(
            "quiz_history_id",
            sa.Integer(),
            sa.ForeignKey("quiz_history.id"),
            nullable=False,
        ),
        sa.Column(
            "score",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "total_correct",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "total_incorrect",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "user_quiz_response",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_quiz_history_id", sa.Integer(), nullable=False),
        sa.Column(
            "question_id",
            sa.Integer(),
            sa.ForeignKey("question.id"),
            nullable=False,
        ),
        sa.Column("selected_answer", sa.Text()),
        sa.Column(
            "is_correct",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column("time_taken", sa.Integer()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

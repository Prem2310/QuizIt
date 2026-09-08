"""Add friend requests and direct duel challenges (friends, custom duels, rematch)."""

from alembic import op
import sqlalchemy as sa

revision = "0003_social_and_challenges"
down_revision = "0002_duel_and_mastery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "friend_request",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("user_data.id"), nullable=False),
        sa.Column("addressee_id", sa.Integer(), sa.ForeignKey("user_data.id"), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("requester_id", "addressee_id", name="uq_friend_request_pair"),
    )
    op.create_index("ix_friend_request_requester_id", "friend_request", ["requester_id"])
    op.create_index("ix_friend_request_addressee_id", "friend_request", ["addressee_id"])

    op.create_table(
        "duel_challenge",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenger_id", sa.Integer(), sa.ForeignKey("user_data.id"), nullable=False),
        sa.Column("opponent_id", sa.Integer(), sa.ForeignKey("user_data.id"), nullable=False),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topic.id")),
        sa.Column("num_questions", sa.Integer(), server_default="10", nullable=False),
        sa.Column("time_per_question", sa.Integer(), server_default="15", nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("duel_match_id", sa.Integer(), sa.ForeignKey("duel_match.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_duel_challenge_challenger_id", "duel_challenge", ["challenger_id"])
    op.create_index("ix_duel_challenge_opponent_id", "duel_challenge", ["opponent_id"])


def downgrade() -> None:
    op.drop_table("duel_challenge")
    op.drop_table("friend_request")

"""Add Matiks features columns to UserData."""

from alembic import op
import sqlalchemy as sa

revision = "0002_matiks_features"
down_revision = "0001_quizit_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add streak and speed metrics columns to user_data table
    with op.batch_alter_table("user_data") as batch_op:
        batch_op.add_column(sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False))
        batch_op.add_column(sa.Column("max_streak", sa.Integer(), server_default="0", nullable=False))
        batch_op.add_column(sa.Column("last_active_date", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("speed_wpm", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("preferred_mode", sa.String(40), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("user_data") as batch_op:
        batch_op.drop_column("preferred_mode")
        batch_op.drop_column("speed_wpm")
        batch_op.drop_column("last_active_date")
        batch_op.drop_column("max_streak")
        batch_op.drop_column("current_streak")

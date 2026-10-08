"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-10-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("creation_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("permission", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "sessions",
        sa.Column("session_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_jti", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("session_id"),
    )
    op.create_index("ix_sessions_token_jti", "sessions", ["token_jti"], unique=True)

    op.create_table(
        "videos",
        sa.Column("video_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("youtube_id", sa.String(length=32), nullable=False),
        sa.Column("upload_by", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("subject_name", sa.String(length=120), nullable=False),
        sa.Column("added_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("length_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["upload_by"], ["users.user_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("video_id"),
    )
    op.create_index("ix_videos_youtube_id", "videos", ["youtube_id"], unique=True)

    op.create_table(
        "watch_items",
        sa.Column("watch_item_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("youtube_id", sa.String(length=32), nullable=False),
        sa.Column("current_time", sa.Float(), nullable=False, server_default="0"),
        sa.Column("save_time", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("average_focus", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["youtube_id"], ["videos.youtube_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("watch_item_id"),
    )

    op.create_table(
        "watch_data",
        sa.Column("watch_data_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("watch_item_id", sa.Integer(), nullable=False),
        sa.Column("log_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("vid_watch_time", sa.Float(), nullable=False, server_default="0"),
        sa.Column("interval", sa.Float(), nullable=False, server_default="1"),
        sa.Column("ticket", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sub_ticket", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["watch_item_id"], ["watch_items.watch_item_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("watch_data_id"),
    )

    op.create_table(
        "log_data",
        sa.Column("log_data_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("watch_data_id", sa.Integer(), nullable=False),
        sa.Column("fps_num", sa.Float(), nullable=False, server_default="1"),
        sa.Column("extraction_type", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["watch_data_id"], ["watch_data.watch_data_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("log_data_id"),
    )

    op.create_table(
        "model_results",
        sa.Column("model_result_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("log_data_id", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("result", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["log_data_id"], ["log_data.log_data_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("model_result_id"),
    )


def downgrade() -> None:
    op.drop_table("model_results")
    op.drop_table("log_data")
    op.drop_table("watch_data")
    op.drop_table("watch_items")
    op.drop_table("videos")
    op.drop_index("ix_sessions_token_jti", table_name="sessions")
    op.drop_table("sessions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

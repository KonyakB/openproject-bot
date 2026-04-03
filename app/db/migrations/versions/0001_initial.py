"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "command_audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("discord_interaction_id", sa.String(length=64), nullable=False),
        sa.Column("discord_user_id", sa.String(length=64), nullable=False),
        sa.Column("discord_username", sa.String(length=128), nullable=False),
        sa.Column("raw_command", sa.Text(), nullable=False),
        sa.Column("parsed_action_json", sa.JSON(), nullable=False),
        sa.Column("validation_result_json", sa.JSON(), nullable=False),
        sa.Column("execution_status", sa.String(length=32), nullable=False),
        sa.Column("openproject_work_package_id", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_command_audit_log_discord_interaction_id", "command_audit_log", ["discord_interaction_id"])
    op.create_index("ix_command_audit_log_discord_user_id", "command_audit_log", ["discord_user_id"])

    op.create_table(
        "pending_confirmations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("discord_user_id", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("parsed_action_json", sa.JSON(), nullable=False),
        sa.Column("validation_result_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_pending_confirmations_discord_user_id", "pending_confirmations", ["discord_user_id"])
    op.create_index("ix_pending_confirmations_expires_at", "pending_confirmations", ["expires_at"])
    op.create_index("ix_pending_confirmations_token", "pending_confirmations", ["token"])

    op.create_table(
        "project_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("human_name", sa.String(length=255), nullable=False),
        sa.Column("openproject_project_id", sa.Integer(), nullable=False),
        sa.Column("openproject_project_identifier", sa.String(length=128), nullable=False),
        sa.Column("aliases_json", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("openproject_project_id"),
    )
    op.create_index("ix_project_mappings_human_name", "project_mappings", ["human_name"])
    op.create_index("ix_project_mappings_openproject_project_id", "project_mappings", ["openproject_project_id"])
    op.create_index("ix_project_mappings_openproject_project_identifier", "project_mappings", ["openproject_project_identifier"])

    op.create_table(
        "project_type_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("openproject_type_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_project_type_mappings_project_id", "project_type_mappings", ["project_id"])
    op.create_index("ix_project_type_mappings_openproject_type_id", "project_type_mappings", ["openproject_type_id"])
    op.create_index("ix_project_type_mappings_name", "project_type_mappings", ["name"])

    op.create_table(
        "field_value_mappings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("field_name", sa.String(length=128), nullable=False),
        sa.Column("field_identifier", sa.Integer(), nullable=False),
        sa.Column("human_value", sa.String(length=255), nullable=False),
        sa.Column("openproject_value", sa.String(length=255), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("aliases_json", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_field_value_mappings_field_name", "field_value_mappings", ["field_name"])
    op.create_index("ix_field_value_mappings_field_identifier", "field_value_mappings", ["field_identifier"])
    op.create_index("ix_field_value_mappings_human_value", "field_value_mappings", ["human_value"])
    op.create_index("ix_field_value_mappings_project_id", "field_value_mappings", ["project_id"])

    op.create_table(
        "metadata_sync_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("metadata_kind", sa.String(length=64), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checksum", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.UniqueConstraint("metadata_kind"),
    )


def downgrade() -> None:
    op.drop_table("metadata_sync_state")
    op.drop_index("ix_field_value_mappings_project_id", table_name="field_value_mappings")
    op.drop_index("ix_field_value_mappings_human_value", table_name="field_value_mappings")
    op.drop_index("ix_field_value_mappings_field_identifier", table_name="field_value_mappings")
    op.drop_index("ix_field_value_mappings_field_name", table_name="field_value_mappings")
    op.drop_table("field_value_mappings")
    op.drop_index("ix_project_type_mappings_name", table_name="project_type_mappings")
    op.drop_index("ix_project_type_mappings_openproject_type_id", table_name="project_type_mappings")
    op.drop_index("ix_project_type_mappings_project_id", table_name="project_type_mappings")
    op.drop_table("project_type_mappings")
    op.drop_index("ix_project_mappings_openproject_project_identifier", table_name="project_mappings")
    op.drop_index("ix_project_mappings_openproject_project_id", table_name="project_mappings")
    op.drop_index("ix_project_mappings_human_name", table_name="project_mappings")
    op.drop_table("project_mappings")
    op.drop_index("ix_pending_confirmations_token", table_name="pending_confirmations")
    op.drop_index("ix_pending_confirmations_expires_at", table_name="pending_confirmations")
    op.drop_index("ix_pending_confirmations_discord_user_id", table_name="pending_confirmations")
    op.drop_table("pending_confirmations")
    op.drop_index("ix_command_audit_log_discord_user_id", table_name="command_audit_log")
    op.drop_index("ix_command_audit_log_discord_interaction_id", table_name="command_audit_log")
    op.drop_table("command_audit_log")

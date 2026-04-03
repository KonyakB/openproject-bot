from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommandAuditLog(Base):
    __tablename__ = "command_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    discord_interaction_id: Mapped[str] = mapped_column(String(64), index=True)
    discord_user_id: Mapped[str] = mapped_column(String(64), index=True)
    discord_username: Mapped[str] = mapped_column(String(128))
    raw_command: Mapped[str] = mapped_column(Text)
    parsed_action_json: Mapped[dict] = mapped_column(JSON)
    validation_result_json: Mapped[dict] = mapped_column(JSON)
    execution_status: Mapped[str] = mapped_column(String(32))
    openproject_work_package_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class PendingConfirmation(Base):
    __tablename__ = "pending_confirmations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    discord_user_id: Mapped[str] = mapped_column(String(64), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    parsed_action_json: Mapped[dict] = mapped_column(JSON)
    validation_result_json: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ProjectMapping(Base):
    __tablename__ = "project_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    human_name: Mapped[str] = mapped_column(String(255), index=True)
    openproject_project_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    openproject_project_identifier: Mapped[str] = mapped_column(String(128), index=True)
    aliases_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ProjectTypeMapping(Base):
    __tablename__ = "project_type_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, index=True)
    openproject_type_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class FieldValueMapping(Base):
    __tablename__ = "field_value_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    field_name: Mapped[str] = mapped_column(String(128), index=True)
    field_identifier: Mapped[int] = mapped_column(Integer, index=True)
    human_value: Mapped[str] = mapped_column(String(255), index=True)
    openproject_value: Mapped[str] = mapped_column(String(255))
    project_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    aliases_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class MetadataSyncState(Base):
    __tablename__ = "metadata_sync_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metadata_kind: Mapped[str] = mapped_column(String(64), unique=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="never")

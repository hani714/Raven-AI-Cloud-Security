"""create byok tables

Revision ID: 20260522_byok_tables
Revises: 20260418_01
Create Date: 2026-05-22 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260522_byok_tables"
down_revision = "20260418_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("providers"):
        op.create_table(
            "providers",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("slug", sa.String(), nullable=False),
            sa.Column("display_name", sa.String(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )

    provider_indexes = {idx["name"] for idx in inspector.get_indexes("providers")} if inspector.has_table("providers") else set()
    if "ux_providers_slug" not in provider_indexes:
        op.create_index("ux_providers_slug", "providers", ["slug"], unique=True)

    if not inspector.has_table("provider_models"):
        op.create_table(
            "provider_models",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("provider_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("model_id", sa.String(), nullable=False),
            sa.Column("display_name", sa.String(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.ForeignKeyConstraint(
                ["provider_id"],
                ["providers.id"],
                ondelete="CASCADE",
            ),
        )

    if not inspector.has_table("user_api_keys"):
        op.create_table(
            "user_api_keys",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("provider_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("label", sa.String(), nullable=True),
            sa.Column("encrypted_key", sa.Text(), nullable=False),
            sa.Column("key_preview", sa.String(length=4), nullable=False),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["provider_id"],
                ["providers.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["model_id"],
                ["provider_models.id"],
                ondelete="CASCADE",
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("user_api_keys"):
        op.drop_table("user_api_keys")

    if inspector.has_table("provider_models"):
        op.drop_table("provider_models")

    if inspector.has_table("providers"):
        provider_indexes = {idx["name"] for idx in inspector.get_indexes("providers")}
        if "ux_providers_slug" in provider_indexes:
            op.drop_index("ux_providers_slug", table_name="providers")
        op.drop_table("providers")

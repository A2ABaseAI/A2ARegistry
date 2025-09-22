"""core schema

Revision ID: 001_core
Revises: 
Create Date: 2025-09-21 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "001_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "oauth_clients",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "client_id", name="uq_oauth_clients_tenant_client"),
    )

    op.create_table(
        "agents",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("publisher_id", sa.String(), nullable=False),
        sa.Column("agent_key", sa.String(), nullable=False),
        sa.Column("latest_version", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "publisher_id", "agent_key", name="uq_agents_pub_key"),
    )
    op.create_index("idx_agents_tenant", "agents", ["tenant_id"])

    op.create_table(
        "agent_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("agent_id", sa.String(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("protocol_version", sa.String(), nullable=False),
        sa.Column("card_json", sa.JSON(), nullable=False),
        sa.Column("card_hash", sa.String(), nullable=False),
        sa.Column("card_url", sa.Text()),
        sa.Column("jwks_url", sa.Text()),
        sa.Column("signature_valid", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("public", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("agent_id", "version", name="uq_agent_versions_unique"),
    )
    op.create_index("idx_agent_versions_agent", "agent_versions", ["agent_id"])

    op.create_table(
        "entitlements",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("scope", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "client_id", "agent_id", "scope", name="uq_entitlements"),
    )
    op.create_index("idx_entitlements_client", "entitlements", ["tenant_id", "client_id", "agent_id"])


def downgrade() -> None:
    op.drop_index("idx_entitlements_client", table_name="entitlements")
    op.drop_table("entitlements")
    op.drop_index("idx_agent_versions_agent", table_name="agent_versions")
    op.drop_table("agent_versions")
    op.drop_index("idx_agents_tenant", table_name="agents")
    op.drop_table("agents")
    op.drop_table("oauth_clients")
    op.drop_table("tenants")



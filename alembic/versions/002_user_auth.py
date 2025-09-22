"""Add user authentication tables

Revision ID: 002_user_auth
Revises: 001_core
Create Date: 2024-01-16 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002_user_auth"
down_revision = "001_core"
branch_labels = None
depends_on = None


def upgrade():
    """Add user authentication tables."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("roles", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("profile_data", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for users table
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"], unique=False)

    # Create user_sessions table
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for user_sessions table
    op.create_index(op.f("ix_user_sessions_user_id"), "user_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_sessions_token_hash"), "user_sessions", ["token_hash"], unique=True)

    # Create user_invitations table
    op.create_table(
        "user_invitations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("invited_by", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        sa.Column("roles", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("invitation_token", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for user_invitations table
    op.create_index(op.f("ix_user_invitations_email"), "user_invitations", ["email"], unique=False)
    op.create_index(op.f("ix_user_invitations_invited_by"), "user_invitations", ["invited_by"], unique=False)
    op.create_index(op.f("ix_user_invitations_tenant_id"), "user_invitations", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_user_invitations_invitation_token"), "user_invitations", ["invitation_token"], unique=True)


def downgrade():
    """Remove user authentication tables."""
    # Drop indexes
    op.drop_index(op.f("ix_user_invitations_invitation_token"), table_name="user_invitations")
    op.drop_index(op.f("ix_user_invitations_tenant_id"), table_name="user_invitations")
    op.drop_index(op.f("ix_user_invitations_invited_by"), table_name="user_invitations")
    op.drop_index(op.f("ix_user_invitations_email"), table_name="user_invitations")

    op.drop_index(op.f("ix_user_sessions_token_hash"), table_name="user_sessions")
    op.drop_index(op.f("ix_user_sessions_user_id"), table_name="user_sessions")

    op.drop_index(op.f("ix_users_tenant_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")

    # Drop tables
    op.drop_table("user_invitations")
    op.drop_table("user_sessions")
    op.drop_table("users")

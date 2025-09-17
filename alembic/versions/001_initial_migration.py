"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2025-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clients table
    op.create_table('clients',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('client_secret', sa.String(), nullable=False),
        sa.Column('redirect_uris', sa.JSON(), nullable=True),
        sa.Column('scopes', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_client_id'), 'clients', ['client_id'], unique=True)
    op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=False)
    op.create_index(op.f('ix_clients_is_active'), 'clients', ['is_active'], unique=False)

    # Create agents table
    op.create_table('agents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('agent_card', sa.JSON(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('location_url', sa.String(), nullable=True),
        sa.Column('location_type', sa.String(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('capabilities', sa.JSON(), nullable=True),
        sa.Column('auth_schemes', sa.JSON(), nullable=True),
        sa.Column('tee_details', sa.JSON(), nullable=True),
        sa.Column('client_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=False)
    op.create_index(op.f('ix_agents_provider'), 'agents', ['provider'], unique=False)
    op.create_index(op.f('ix_agents_is_public'), 'agents', ['is_public'], unique=False)
    op.create_index(op.f('ix_agents_is_active'), 'agents', ['is_active'], unique=False)

    # Create client_entitlements table
    op.create_table('client_entitlements',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('scopes', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_client_entitlements_client_id'), 'client_entitlements', ['client_id'], unique=False)
    op.create_index(op.f('ix_client_entitlements_agent_id'), 'client_entitlements', ['agent_id'], unique=False)
    op.create_index(op.f('ix_client_entitlements_is_active'), 'client_entitlements', ['is_active'], unique=False)

    # Create peer_registries table
    op.create_table('peer_registries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('base_url', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('auth_token', sa.String(), nullable=True),
        sa.Column('sync_enabled', sa.Boolean(), nullable=True),
        sa.Column('sync_interval_minutes', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_peer_registries_name'), 'peer_registries', ['name'], unique=False)
    op.create_index(op.f('ix_peer_registries_base_url'), 'peer_registries', ['base_url'], unique=True)
    op.create_index(op.f('ix_peer_registries_sync_enabled'), 'peer_registries', ['sync_enabled'], unique=False)
    op.create_index(op.f('ix_peer_registries_is_active'), 'peer_registries', ['is_active'], unique=False)

    # Create peer_syncs table
    op.create_table('peer_syncs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('peer_registry_id', sa.String(), nullable=False),
        sa.Column('sync_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('agents_synced', sa.Integer(), nullable=True),
        sa.Column('agents_added', sa.Integer(), nullable=True),
        sa.Column('agents_updated', sa.Integer(), nullable=True),
        sa.Column('agents_removed', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['peer_registry_id'], ['peer_registries.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_peer_syncs_peer_registry_id'), 'peer_syncs', ['peer_registry_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_peer_syncs_peer_registry_id'), table_name='peer_syncs')
    op.drop_table('peer_syncs')
    
    op.drop_index(op.f('ix_peer_registries_is_active'), table_name='peer_registries')
    op.drop_index(op.f('ix_peer_registries_sync_enabled'), table_name='peer_registries')
    op.drop_index(op.f('ix_peer_registries_base_url'), table_name='peer_registries')
    op.drop_index(op.f('ix_peer_registries_name'), table_name='peer_registries')
    op.drop_table('peer_registries')
    
    op.drop_index(op.f('ix_client_entitlements_is_active'), table_name='client_entitlements')
    op.drop_index(op.f('ix_client_entitlements_agent_id'), table_name='client_entitlements')
    op.drop_index(op.f('ix_client_entitlements_client_id'), table_name='client_entitlements')
    op.drop_table('client_entitlements')
    
    op.drop_index(op.f('ix_agents_is_active'), table_name='agents')
    op.drop_index(op.f('ix_agents_is_public'), table_name='agents')
    op.drop_index(op.f('ix_agents_provider'), table_name='agents')
    op.drop_index(op.f('ix_agents_name'), table_name='agents')
    op.drop_table('agents')
    
    op.drop_index(op.f('ix_clients_is_active'), table_name='clients')
    op.drop_index(op.f('ix_clients_name'), table_name='clients')
    op.drop_index(op.f('ix_clients_client_id'), table_name='clients')
    op.drop_table('clients')

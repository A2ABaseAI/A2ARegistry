-- A2A Agent Registry Database Initialization
-- This script is run automatically when the database container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created by Alembic migrations, but we can add additional ones here

-- Performance indexes for common queries
-- (These are in addition to the ones created by SQLAlchemy/Alembic)

-- Agent search optimization
CREATE INDEX IF NOT EXISTS idx_agents_search_text ON agents USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX IF NOT EXISTS idx_agents_tags_gin ON agents USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_agents_provider_active ON agents(provider, is_active) WHERE is_public = true;

-- Client lookup optimization  
CREATE INDEX IF NOT EXISTS idx_clients_client_id_active ON clients(client_id, is_active);

-- Peer registry optimization
CREATE INDEX IF NOT EXISTS idx_peers_sync_status ON peer_registries(sync_enabled, is_active, last_sync_at);

-- Entitlements optimization
CREATE INDEX IF NOT EXISTS idx_entitlements_client_agent ON client_entitlements(client_id, agent_id, is_active);

-- Log retention policy (optional)
-- You can uncomment this if you want automatic cleanup of old sync logs
-- CREATE OR REPLACE FUNCTION cleanup_old_peer_syncs()
-- RETURNS void AS $$
-- BEGIN
--     DELETE FROM peer_syncs WHERE created_at < NOW() - INTERVAL '30 days';
-- END;
-- $$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

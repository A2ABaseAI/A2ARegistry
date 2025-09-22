#!/bin/bash

# A2A Agent Registry Restore Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/backups/a2a-registry"

echo -e "${GREEN}🔄 Starting A2A Agent Registry Restore${NC}"

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Please provide a backup file${NC}"
    echo -e "${YELLOW}Usage: $0 <backup_file.tar.gz>${NC}"
    echo -e "${YELLOW}Available backups:${NC}"
    ls -la "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}📁 Backup file: $BACKUP_FILE${NC}"

# Confirm restore operation
echo -e "${RED}⚠️  WARNING: This will restore the A2A Agent Registry from backup${NC}"
echo -e "${RED}⚠️  This operation will overwrite existing data!${NC}"
read -p "Are you sure you want to continue? (yes/NO): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}❌ Restore cancelled${NC}"
    exit 0
fi

# Stop services
echo -e "${YELLOW}🛑 Stopping services...${NC}"
docker-compose -f "$COMPOSE_FILE" down

# Extract backup
echo -e "${YELLOW}📦 Extracting backup...${NC}"
temp_dir="/tmp/a2a_restore_$$"
mkdir -p "$temp_dir"
tar xzf "$BACKUP_FILE" -C "$temp_dir"

backup_name=$(basename "$BACKUP_FILE" .tar.gz)
backup_path="$temp_dir/$backup_name"

if [ ! -d "$backup_path" ]; then
    echo -e "${RED}❌ Invalid backup format${NC}"
    rm -rf "$temp_dir"
    exit 1
fi

echo -e "${GREEN}✅ Backup extracted to $backup_path${NC}"

# Start services (without registry)
echo -e "${YELLOW}🚀 Starting infrastructure services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d db redis opensearch

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check database health
if ! docker-compose -f "$COMPOSE_FILE" exec db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${RED}❌ Database is not ready${NC}"
    rm -rf "$temp_dir"
    exit 1
fi

# Restore database
echo -e "${YELLOW}🗄️ Restoring database...${NC}"
if [ -f "$backup_path/database.sql" ]; then
    docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d a2a_registry < "$backup_path/database.sql"
    echo -e "${GREEN}✅ Database restored${NC}"
else
    echo -e "${RED}❌ Database backup not found${NC}"
    rm -rf "$temp_dir"
    exit 1
fi

# Stop services to restore volumes
echo -e "${YELLOW}🛑 Stopping services for volume restore...${NC}"
docker-compose -f "$COMPOSE_FILE" down

# Restore Redis data
echo -e "${YELLOW}🔴 Restoring Redis data...${NC}"
if [ -f "$backup_path/redis_data.tar.gz" ]; then
    docker run --rm -v a2a-registry_redis_data:/data -v "$backup_path":/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
    echo -e "${GREEN}✅ Redis data restored${NC}"
else
    echo -e "${RED}❌ Redis backup not found${NC}"
fi

# Restore OpenSearch data (optional)
echo -e "${YELLOW}🔍 Restoring OpenSearch data...${NC}"
if [ -f "$backup_path/elasticsearch_data.tar.gz" ]; then
    docker run --rm -v a2a-registry_elasticsearch_data:/data -v "$backup_path":/backup alpine tar xzf /backup/elasticsearch_data.tar.gz -C /data || true
    echo -e "${GREEN}✅ OpenSearch data restored (if applicable)${NC}"
fi

# Start all services
echo -e "${YELLOW}🚀 Starting all services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}🔍 Checking service health...${NC}"

# Check registry health
if curl -f http://localhost:8000/health/live > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Registry is healthy${NC}"
else
    echo -e "${RED}❌ Registry health check failed${NC}"
    docker-compose -f "$COMPOSE_FILE" logs registry
fi

# Check database health
if docker-compose -f "$COMPOSE_FILE" exec db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${RED}❌ Database health check failed${NC}"
fi

# Check Redis health
if docker-compose -f "$COMPOSE_FILE" exec redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis health check failed${NC}"
fi

# Check OpenSearch health
if curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OpenSearch is healthy${NC}"
else
    echo -e "${RED}❌ OpenSearch health check failed${NC}"
fi

# Clean up temporary files
rm -rf "$temp_dir"

# Show service status
echo -e "${GREEN}🎉 Restore completed successfully!${NC}"
echo -e "${YELLOW}📊 Service Status:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

echo -e "${YELLOW}🌐 Service URLs:${NC}"
echo -e "  Registry API: http://localhost:8000"
echo -e "  API Documentation: http://localhost:8000/docs"
echo -e "  Health Check: http://localhost:8000/health"

echo -e "${GREEN}✅ A2A Agent Registry has been restored from backup!${NC}"

#!/bin/bash

# A2A Agent Registry Backup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/backups/a2a-registry"
RETENTION_DAYS=30

echo -e "${GREEN}💾 Starting A2A Agent Registry Backup${NC}"

# Check if Docker Compose is running
if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    echo -e "${RED}❌ Services are not running. Please start the services first.${NC}"
    exit 1
fi

# Create backup directory
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_path="$BACKUP_DIR/backup_$timestamp"
mkdir -p "$backup_path"

echo -e "${YELLOW}📁 Creating backup directory: $backup_path${NC}"

# Backup database
echo -e "${YELLOW}🗄️ Backing up database...${NC}"
docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres a2a_registry > "$backup_path/database.sql"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database backup completed${NC}"
else
    echo -e "${RED}❌ Database backup failed${NC}"
    exit 1
fi

# Backup Redis data
echo -e "${YELLOW}🔴 Backing up Redis data...${NC}"
docker run --rm -v a2a-registry_redis_data:/data -v "$backup_path":/backup alpine tar czf /backup/redis_data.tar.gz -C /data .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Redis backup completed${NC}"
else
    echo -e "${RED}❌ Redis backup failed${NC}"
    exit 1
fi

# Backup Elasticsearch data
echo -e "${YELLOW}🔍 Backing up Elasticsearch data...${NC}"
docker run --rm -v a2a-registry_elasticsearch_data:/data -v "$backup_path":/backup alpine tar czf /backup/elasticsearch_data.tar.gz -C /data .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Elasticsearch backup completed${NC}"
else
    echo -e "${RED}❌ Elasticsearch backup failed${NC}"
    exit 1
fi

# Backup configuration files
echo -e "${YELLOW}⚙️ Backing up configuration files...${NC}"
cp -r . "$backup_path/config/" 2>/dev/null || true

# Create backup manifest
echo -e "${YELLOW}📋 Creating backup manifest...${NC}"
cat > "$backup_path/manifest.txt" << EOF
A2A Agent Registry Backup
========================
Backup Date: $(date)
Backup Path: $backup_path
Services Status:
$(docker-compose -f "$COMPOSE_FILE" ps)

Database Size: $(du -h "$backup_path/database.sql" | cut -f1)
Redis Data Size: $(du -h "$backup_path/redis_data.tar.gz" | cut -f1)
Elasticsearch Data Size: $(du -h "$backup_path/elasticsearch_data.tar.gz" | cut -f1)
Total Backup Size: $(du -sh "$backup_path" | cut -f1)
EOF

# Compress backup
echo -e "${YELLOW}📦 Compressing backup...${NC}"
cd "$BACKUP_DIR"
tar czf "backup_$timestamp.tar.gz" "backup_$timestamp"
rm -rf "backup_$timestamp"

backup_file="backup_$timestamp.tar.gz"
backup_size=$(du -h "$backup_file" | cut -f1)

echo -e "${GREEN}✅ Backup completed successfully!${NC}"
echo -e "${YELLOW}📊 Backup Details:${NC}"
echo -e "  File: $backup_file"
echo -e "  Size: $backup_size"
echo -e "  Location: $BACKUP_DIR"

# Clean up old backups
echo -e "${YELLOW}🧹 Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

remaining_backups=$(ls -1 "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Cleanup completed. $remaining_backups backups remaining.${NC}"

echo -e "${GREEN}🎉 Backup process completed successfully!${NC}"

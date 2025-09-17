#!/bin/bash

# A2A Agent Registry Production Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="env.prod"
BACKUP_DIR="/backups/a2a-registry"
LOG_DIR="/var/log/a2a-registry"

echo -e "${GREEN}🚀 Starting A2A Agent Registry Production Deployment${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Environment file $ENV_FILE not found${NC}"
    echo -e "${YELLOW}Please create $ENV_FILE with your production configuration${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
sudo mkdir -p "$BACKUP_DIR"
sudo mkdir -p "$LOG_DIR"
sudo chown -R $(whoami):$(whoami) "$BACKUP_DIR"
sudo chown -R $(whoami):$(whoami) "$LOG_DIR"

# Backup existing data if it exists
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    echo -e "${YELLOW}💾 Creating backup of existing data...${NC}"
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_path="$BACKUP_DIR/backup_$timestamp"
    
    mkdir -p "$backup_path"
    
    # Backup database
    docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres a2a_registry > "$backup_path/database.sql"
    
    # Backup volumes
    docker run --rm -v a2a-registry_postgres_data:/data -v "$backup_path":/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
    docker run --rm -v a2a-registry_redis_data:/data -v "$backup_path":/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    docker run --rm -v a2a-registry_elasticsearch_data:/data -v "$backup_path":/backup alpine tar czf /backup/elasticsearch_data.tar.gz -C /data .
    
    echo -e "${GREEN}✅ Backup created at $backup_path${NC}"
fi

# Pull latest images
echo -e "${YELLOW}📥 Pulling latest Docker images...${NC}"
docker-compose -f "$COMPOSE_FILE" pull

# Build application image
echo -e "${YELLOW}🔨 Building application image...${NC}"
docker-compose -f "$COMPOSE_FILE" build registry

# Run database migrations
echo -e "${YELLOW}🗄️ Running database migrations...${NC}"
docker-compose -f "$COMPOSE_FILE" run --rm registry alembic upgrade head

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
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
    exit 1
fi

# Check database health
if docker-compose -f "$COMPOSE_FILE" exec db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${RED}❌ Database health check failed${NC}"
    exit 1
fi

# Check Redis health
if docker-compose -f "$COMPOSE_FILE" exec redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis health check failed${NC}"
    exit 1
fi

# Check Elasticsearch health
if curl -f http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Elasticsearch is healthy${NC}"
else
    echo -e "${RED}❌ Elasticsearch health check failed${NC}"
    exit 1
fi

# Initialize sample data (optional)
read -p "Do you want to initialize sample data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📊 Initializing sample data...${NC}"
    docker-compose -f "$COMPOSE_FILE" exec registry python scripts/init_db.py
fi

# Show service status
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${YELLOW}📊 Service Status:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

echo -e "${YELLOW}🌐 Service URLs:${NC}"
echo -e "  Registry API: http://localhost:8000"
echo -e "  API Documentation: http://localhost:8000/docs"
echo -e "  Health Check: http://localhost:8000/health"
echo -e "  Metrics: http://localhost:8000/metrics"
echo -e "  Prometheus: http://localhost:9090"
echo -e "  Grafana: http://localhost:3000"

echo -e "${YELLOW}📝 Next Steps:${NC}"
echo -e "  1. Configure SSL certificates in ./ssl/"
echo -e "  2. Update DNS to point to your server"
echo -e "  3. Configure firewall rules"
echo -e "  4. Set up monitoring alerts"
echo -e "  5. Review security settings"

echo -e "${GREEN}✅ A2A Agent Registry is now running in production!${NC}"

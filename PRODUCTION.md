# A2A Agent Registry - Production Deployment Guide

This guide covers deploying the A2A Agent Registry in a production environment with enterprise-grade features including monitoring, security, backup, and high availability.

## 🏗️ Production Architecture

### Components
- **A2A Registry**: FastAPI application with Gunicorn workers
- **PostgreSQL**: Primary database with connection pooling
- **Redis**: Caching and session storage
- **Elasticsearch**: Search indexing and analytics
- **Nginx**: Reverse proxy with SSL termination and rate limiting
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

### Security Features
- **OAuth 2.0**: Client credentials flow for authentication
- **JWT Tokens**: Secure token-based authentication
- **Rate Limiting**: Per-client and per-endpoint rate limits
- **Security Headers**: HSTS, CSP, XSS protection
- **Input Validation**: Comprehensive request validation
- **Audit Logging**: Security event logging

### Monitoring & Observability
- **Structured Logging**: JSON logs with request tracing
- **Metrics**: Prometheus metrics for all operations
- **Health Checks**: Comprehensive health monitoring
- **Distributed Tracing**: Request ID tracking
- **Performance Monitoring**: Response time and throughput metrics

## 🚀 Quick Production Deployment

### Prerequisites
- Docker and Docker Compose
- SSL certificates (for HTTPS)
- Domain name configured
- Server with minimum 4GB RAM, 2 CPU cores

### 1. Clone and Configure
```bash
git clone https://github.com/A2AReg/a2a-registry.git
cd a2a-registry

# Copy production environment file
cp env.prod .env.prod

# Edit configuration
nano .env.prod
```

### 2. Configure SSL Certificates
```bash
mkdir -p ssl
# Copy your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
```

### 3. Deploy
```bash
# Run deployment script
./scripts/deploy.sh
```

### 4. Verify Deployment
```bash
# Check service health
curl https://your-domain.com/health

# Check metrics
curl https://your-domain.com/metrics

# Access API documentation
open https://your-domain.com/docs
```

## 🔧 Production Configuration

### Environment Variables

#### Core Application
```bash
APP_NAME="A2A Agent Registry"
APP_VERSION="1.0.0"
DEBUG=false
```

#### Database
```bash
DATABASE_URL="postgresql://user:password@db:5432/a2a_registry"
```

#### Security
```bash
SECRET_KEY="your-very-secure-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Registry Settings
```bash
REGISTRY_BASE_URL="https://your-domain.com"
MAX_AGENTS_PER_CLIENT=1000
ENABLE_FEDERATION=true
```

### SSL Configuration

#### Nginx SSL Settings
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
```

#### Certificate Management
- Use Let's Encrypt for free SSL certificates
- Implement certificate auto-renewal
- Monitor certificate expiration

### Database Configuration

#### PostgreSQL Settings
```sql
-- Connection pooling
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB

-- Performance tuning
random_page_cost = 1.1
effective_io_concurrency = 200
```

#### Backup Strategy
- Automated daily backups
- Point-in-time recovery
- Cross-region backup replication

## 📊 Monitoring & Alerting

### Prometheus Metrics

#### Key Metrics to Monitor
- `a2a_registry_requests_total` - Request count by endpoint
- `a2a_registry_request_duration_seconds` - Request latency
- `a2a_registry_agents_total` - Agent count by status
- `a2a_registry_search_queries_total` - Search query count
- `a2a_registry_peer_syncs_total` - Federation sync count

#### Alerting Rules
```yaml
groups:
  - name: a2a_registry
    rules:
      - alert: HighErrorRate
        expr: rate(a2a_registry_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(a2a_registry_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
```

### Grafana Dashboards

#### Registry Overview Dashboard
- Request rate and latency
- Agent registration trends
- Search performance
- Federation sync status
- System resource usage

#### Security Dashboard
- Authentication attempts
- Rate limit violations
- Suspicious activity
- Failed requests

## 🔒 Security Hardening

### Network Security
- Firewall configuration
- VPN access for admin functions
- Network segmentation
- DDoS protection

### Application Security
- Regular security updates
- Vulnerability scanning
- Penetration testing
- Code security reviews

### Data Protection
- Encryption at rest
- Encryption in transit
- Data retention policies
- GDPR compliance

## 🔄 Backup & Recovery

### Automated Backups
```bash
# Daily backup cron job
0 2 * * * /path/to/a2a-registry/scripts/backup.sh
```

### Backup Verification
```bash
# Test restore process
./scripts/restore.sh /backups/a2a-registry/backup_20250116_020000.tar.gz
```

### Disaster Recovery
- Multi-region deployment
- Automated failover
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)

## 📈 Performance Optimization

### Application Tuning
- Worker process optimization
- Connection pooling
- Caching strategies
- Database query optimization

### Infrastructure Scaling
- Horizontal scaling with load balancers
- Vertical scaling for resource-intensive workloads
- Auto-scaling based on metrics
- CDN for static content

### Monitoring Performance
- APM (Application Performance Monitoring)
- Database performance monitoring
- Infrastructure monitoring
- User experience monitoring

## 🚨 Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart registry
```

#### Database Connection Issues
```bash
# Check database health
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres

# Check connection pool
docker-compose -f docker-compose.prod.yml exec registry python -c "
from app.database import engine
print(engine.pool.status())
"
```

#### Search Index Issues
```bash
# Recreate search index
docker-compose -f docker-compose.prod.yml exec registry python -c "
from app.services.search_service import SearchService
from app.database import SessionLocal
db = SessionLocal()
search_service = SearchService(db)
search_service.create_index()
"
```

### Log Analysis
```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f registry

# View error logs
tail -f /var/log/a2a-registry/error.log

# Search logs
grep "ERROR" /var/log/a2a-registry/app.log | tail -20
```

## 🔧 Maintenance

### Regular Maintenance Tasks
- Security updates
- Database maintenance
- Log rotation
- Backup verification
- Performance monitoring

### Update Procedures
```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml build registry
docker-compose -f docker-compose.prod.yml up -d registry

# Database migrations
docker-compose -f docker-compose.prod.yml exec registry alembic upgrade head
```

### Health Monitoring
- Automated health checks
- Alert notifications
- Performance baselines
- Capacity planning

## 📞 Support

### Documentation
- API Documentation: `/docs`
- Health Status: `/health`
- Metrics: `/metrics`

### Monitoring URLs
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Registry API: http://localhost:8000

### Contact Information
- GitHub Issues: [Report bugs and request features](https://github.com/A2AReg/a2a-registry/issues)
- Community: [A2A Discussions](https://github.com/a2aproject/A2A/discussions)

---

This production deployment provides enterprise-grade reliability, security, and monitoring for the A2A Agent Registry. Regular maintenance and monitoring are essential for optimal performance and security.

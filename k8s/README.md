# A2A Registry Kubernetes Deployment

Complete Kubernetes deployment for the A2A Agent Registry stack including Registry, Runner, PostgreSQL, Redis, and OpenSearch.

## Architecture

```
┌─────────────┐
│   Ingress   │ (Optional - external access)
└──────┬──────┘
       │
       ├──► Registry (FastAPI) ──► PostgreSQL
       │                          └──► Redis
       │                          └──► OpenSearch
       │
       ├──► Runner (FastAPI) ────► Registry
       │
       └──► UI (Next.js) ───────► Registry
```

## Prerequisites

1. Kubernetes cluster (v1.20+)
2. `kubectl` configured to access your cluster
3. `kustomize` or `kubectl` with kustomize support
4. Storage class configured for PersistentVolumes (default: `standard`)
5. Optional: NGINX Ingress Controller or your ingress controller of choice
6. Optional: cert-manager for TLS certificates

## Quick Start

### 1. Update Secrets

**⚠️ IMPORTANT: Update secrets before deploying!**

Edit `secrets.yaml` and change all default passwords and keys:

```bash
# Edit secrets.yaml
nano secrets.yaml

# Key secrets to update:
# - SECRET_KEY: Generate a strong random key
# - POSTGRES_PASSWORD: Strong database password
# - OPENSEARCH_INITIAL_ADMIN_PASSWORD: Strong OpenSearch password
# - API_KEYS: Your production API keys
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Build Docker Images

Build and push your Docker images to a registry accessible by your cluster:

```bash
# Build Registry image
docker build -f k8s/Dockerfile.registry -t your-registry/a2a-registry:latest .
docker push your-registry/a2a-registry:latest

# Build Runner image
docker build -f k8s/Dockerfile.runner -t your-registry/a2a-runner:latest .
docker push your-registry/a2a-runner:latest

# Build UI image (if deploying UI)
cd ui
docker build -t your-registry/a2a-ui:latest .
docker push your-registry/a2a-ui:latest
cd ..
```

Update image names in deployment files:
- `registry-deployment.yaml`: Change `a2a-registry:latest`
- `runner-deployment.yaml`: Change `a2a-runner:latest`
- `ui-deployment.yaml`: Change `a2a-ui:latest`

### 3. Update Configuration

1. **Update storage class** in all PVC files if needed:
   ```yaml
   storageClassName: standard  # Change to your storage class
   ```

2. **Update ConfigMap** values if needed:
   ```bash
   nano configmap.yaml
   ```

3. **Update Ingress** hostnames (if different from default):
   ```bash
   nano ingress.yaml
   # Default: api.a2areg.com, runner.a2areg.com, a2areg.com
   ```

### 4. Deploy

#### Option A: Using kustomize

```bash
kubectl apply -k k8s/
```

#### Option B: Manual deployment

```bash
# Deploy in order
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/opensearch-deployment.yaml

# Wait for dependencies to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n a2a-registry --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n a2a-registry --timeout=300s
kubectl wait --for=condition=ready pod -l app=opensearch -n a2a-registry --timeout=300s

# Deploy applications
kubectl apply -f k8s/registry-deployment.yaml
kubectl apply -f k8s/runner-deployment.yaml
kubectl apply -f k8s/ui-deployment.yaml  # Optional

# Deploy ingress (optional)
kubectl apply -f k8s/ingress.yaml
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n a2a-registry

# Check services
kubectl get svc -n a2a-registry

# Check ingress (if deployed)
kubectl get ingress -n a2a-registry

# View registry logs
kubectl logs -f -l app=registry -n a2a-registry

# View runner logs
kubectl logs -f -l app=runner -n a2a-registry
```

## Accessing Services

### Port Forwarding (Development/Testing)

```bash
# Registry
kubectl port-forward -n a2a-registry svc/registry 8000:8000

# Runner
kubectl port-forward -n a2a-registry svc/runner 8001:8001

# UI
kubectl port-forward -n a2a-registry svc/ui 3000:3000
```

Then access:
- Registry: http://localhost:8000
- Runner: http://localhost:8001
- UI: http://localhost:3000

### Using Ingress (Production)

If Ingress is configured, access via:
- Registry API: https://api.a2areg.com
- Runner: https://runner.a2areg.com
- UI: https://a2areg.com

## Configuration

### Environment Variables

Key environment variables are set in:
- **ConfigMap**: Non-sensitive configuration
- **Secrets**: Sensitive data (passwords, keys)

See `configmap.yaml` and `secrets.yaml` for all available options.

### Scaling

The deployments use HorizontalPodAutoscaler (HPA) for automatic scaling:

- **Registry**: 2-10 replicas (scales on CPU/Memory)
- **Runner**: 2-10 replicas (scales on CPU/Memory)

Adjust HPA settings in:
- `registry-deployment.yaml`
- `runner-deployment.yaml`

### Resource Limits

Default resource requests/limits:
- **Registry**: 512Mi-2Gi memory, 500m-2000m CPU
- **Runner**: 512Mi-2Gi memory, 500m-2000m CPU
- **PostgreSQL**: 256Mi-1Gi memory, 250m-1000m CPU
- **Redis**: 128Mi-512Mi memory, 100m-500m CPU
- **OpenSearch**: 1Gi-2Gi memory, 500m-2000m CPU

Adjust based on your cluster capacity and load.

## Persistent Storage

The following services use PersistentVolumes:
- **PostgreSQL**: 20Gi (database data)
- **Redis**: 10Gi (AOF persistence)
- **OpenSearch**: 50Gi (index data)

Backup these volumes regularly in production!

## Health Checks

All services include:
- **Liveness probes**: Restart pods if unhealthy
- **Readiness probes**: Remove from service endpoints if not ready

Probe endpoints:
- Registry: `/health/live` (liveness), `/health/ready` (readiness)
- Runner: `/health` (both)
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- OpenSearch: `/_cluster/health`

## Troubleshooting

### Check pod status
```bash
kubectl describe pod <pod-name> -n a2a-registry
```

### View logs
```bash
# Registry
kubectl logs -l app=registry -n a2a-registry --tail=100

# Runner
kubectl logs -l app=runner -n a2a-registry --tail=100

# Database
kubectl logs -l app=postgres -n a2a-registry
```

### Check events
```bash
kubectl get events -n a2a-registry --sort-by='.lastTimestamp'
```

### Common Issues

1. **Pods not starting**: Check resource limits and node capacity
2. **Database connection errors**: Wait for PostgreSQL to be ready (init containers handle this)
3. **OpenSearch memory issues**: Increase memory limits or use larger nodes
4. **Image pull errors**: Ensure images are pushed to accessible registry

## Backup & Restore

### Database Backup
```bash
# Get PostgreSQL pod name
POSTGRES_POD=$(kubectl get pod -l app=postgres -n a2a-registry -o jsonpath='{.items[0].metadata.name}')

# Backup
kubectl exec -n a2a-registry $POSTGRES_POD -- pg_dump -U postgres a2a_registry > backup.sql
```

### Restore
```bash
kubectl exec -i -n a2a-registry $POSTGRES_POD -- psql -U postgres a2a_registry < backup.sql
```

## Upgrading

1. Build and push new images
2. Update image tags in deployment files
3. Apply updated deployments:
   ```bash
   kubectl rollout restart deployment/registry -n a2a-registry
   kubectl rollout restart deployment/runner -n a2a-registry
   ```

## Cleanup

To remove all resources:
```bash
kubectl delete namespace a2a-registry
```

**⚠️ Warning**: This deletes all data including PersistentVolumes!

## Production Recommendations

1. **Use external databases**: Consider managed PostgreSQL/Redis services
2. **External OpenSearch**: Use managed OpenSearch service for better reliability
3. **Secrets management**: Use external secrets manager (e.g., Vault, AWS Secrets Manager)
4. **Monitoring**: Add Prometheus/Grafana for monitoring
5. **Logging**: Add centralized logging (e.g., ELK, Loki)
6. **Backup**: Set up automated backups for PersistentVolumes
7. **TLS**: Use cert-manager for automatic TLS certificate management
8. **Network policies**: Add NetworkPolicies for pod-to-pod communication restrictions
9. **Resource quotas**: Set namespace resource quotas
10. **PodDisruptionBudgets**: Add PDBs for high availability

## Support

For issues or questions:
- Check logs: `kubectl logs -l app=<service> -n a2a-registry`
- Review documentation in repository root
- Open an issue on GitHub


#!/bin/bash
# Quick deployment script for A2A Registry on Kubernetes

set -e

echo "🚀 Deploying A2A Registry to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if namespace exists
if kubectl get namespace a2a-registry &> /dev/null; then
    echo "⚠️  Namespace 'a2a-registry' already exists"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Step 1: Deploying namespace..."
kubectl apply -f namespace.yaml

echo ""
echo "Step 2: Deploying ConfigMaps..."
kubectl apply -f configmap.yaml

echo ""
echo "⚠️  IMPORTANT: Review and update secrets.yaml before continuing!"
echo "   Update: SECRET_KEY, POSTGRES_PASSWORD, DATABASE_URL, API_KEYS"
read -p "Press Enter after updating secrets.yaml..."

echo ""
echo "Step 3: Deploying Secrets..."
kubectl apply -f secrets.yaml

echo ""
echo "Step 4: Deploying PostgreSQL..."
kubectl apply -f postgres-deployment.yaml
echo "   Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n a2a-registry --timeout=300s || echo "⚠️  PostgreSQL may still be starting"

echo ""
echo "Step 5: Deploying Redis..."
kubectl apply -f redis-deployment.yaml
echo "   Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n a2a-registry --timeout=300s || echo "⚠️  Redis may still be starting"

echo ""
echo "Step 6: Deploying OpenSearch..."
kubectl apply -f opensearch-deployment.yaml
echo "   Waiting for OpenSearch to be ready..."
kubectl wait --for=condition=ready pod -l app=opensearch -n a2a-registry --timeout=300s || echo "⚠️  OpenSearch may still be starting"

echo ""
echo "Step 7: Deploying Registry..."
kubectl apply -f registry-deployment.yaml

echo ""
echo "Step 8: Deploying Runner..."
kubectl apply -f runner-deployment.yaml

echo ""
echo "Step 9: Deploying UI (optional)..."
read -p "Deploy UI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl apply -f ui-deployment.yaml
fi

echo ""
echo "Step 10: Checking deployment status..."
sleep 5
kubectl get pods -n a2a-registry

echo ""
echo "✅ Deployment complete!"
echo ""
echo "To view logs:"
echo "  kubectl logs -l app=registry -n a2a-registry"
echo "  kubectl logs -l app=runner -n a2a-registry"
echo ""
echo "To port-forward services:"
echo "  kubectl port-forward -n a2a-registry svc/registry 8000:8000"
echo "  kubectl port-forward -n a2a-registry svc/runner 8001:8001"
echo ""
echo "To check status:"
echo "  kubectl get all -n a2a-registry"


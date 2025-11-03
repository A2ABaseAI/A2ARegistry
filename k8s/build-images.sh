#!/bin/bash
# Build and publish Docker images to GitHub Container Registry
# Usage: ./build-images.sh [tag] [--push]
#   tag: Docker image tag (default: latest)
#   --push: Push images to registry (default: only build)

set -e

# Configuration
GITHUB_USER="a2areg"  # Must be lowercase for Docker
GITHUB_REPO="a2a-registry"
REGISTRY="ghcr.io"
IMAGE_TAG="${1:-latest}"
PUSH_IMAGES="${2:-}"

# Full image names
REGISTRY_IMAGE="${REGISTRY}/${GITHUB_USER}/${GITHUB_REPO}/registry:${IMAGE_TAG}"
RUNNER_IMAGE="${REGISTRY}/${GITHUB_USER}/${GITHUB_REPO}/runner:${IMAGE_TAG}"
UI_IMAGE="${REGISTRY}/${GITHUB_USER}/${GITHUB_REPO}/ui:${IMAGE_TAG}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Building A2A Registry Docker Images${NC}"
echo -e "${BLUE}Registry: ${REGISTRY_IMAGE}${NC}"
echo -e "${BLUE}Runner: ${RUNNER_IMAGE}${NC}"
echo -e "${BLUE}UI: ${UI_IMAGE}${NC}"
echo ""

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Build Registry image
echo -e "${GREEN}📦 Building Registry image...${NC}"
docker build \
  -f registry/Dockerfile.registry \
  -t "${REGISTRY_IMAGE}" \
  -t "${GITHUB_USER}/${GITHUB_REPO}-registry:${IMAGE_TAG}" \
  -t "a2a-registry:latest" \
  .
echo -e "${GREEN}✅ Registry image built${NC}"
echo ""

# Build Runner image
echo -e "${GREEN}📦 Building Runner image...${NC}"
docker build \
  -f runner/Dockerfile.runner \
  -t "${RUNNER_IMAGE}" \
  -t "${GITHUB_USER}/${GITHUB_REPO}-runner:${IMAGE_TAG}" \
  -t "a2a-runner:latest" \
  .
echo -e "${GREEN}✅ Runner image built${NC}"
echo ""

# Build UI image (from project root to include SDK)
echo -e "${GREEN}📦 Building UI image...${NC}"
docker build \
  -f ui/Dockerfile \
  -t "${UI_IMAGE}" \
  -t "${GITHUB_USER}/${GITHUB_REPO}-ui:${IMAGE_TAG}" \
  -t "a2a-ui:latest" \
  .
echo -e "${GREEN}✅ UI image built${NC}"
echo ""

# Push images if --push flag is set
if [ "${PUSH_IMAGES}" = "--push" ]; then
  echo -e "${YELLOW}📤 Pushing images to ${REGISTRY}...${NC}"
  
  # Check if user is logged in to GitHub Container Registry
  if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}⚠️  Not logged in to GitHub Container Registry${NC}"
    echo -e "${YELLOW}Please login with: docker login ${REGISTRY}${NC}"
    echo -e "${YELLOW}Or use a GitHub Personal Access Token (PAT) with package write permissions${NC}"
    exit 1
  fi
  
  echo -e "${GREEN}📤 Pushing Registry image...${NC}"
  docker push "${REGISTRY_IMAGE}"
  echo -e "${GREEN}✅ Registry image pushed${NC}"
  
  echo -e "${GREEN}📤 Pushing Runner image...${NC}"
  docker push "${RUNNER_IMAGE}"
  echo -e "${GREEN}✅ Runner image pushed${NC}"
  
  echo -e "${GREEN}📤 Pushing UI image...${NC}"
  docker push "${UI_IMAGE}"
  echo -e "${GREEN}✅ UI image pushed${NC}"
  
  echo ""
  echo -e "${GREEN}🎉 All images pushed successfully!${NC}"
  echo ""
  echo -e "${BLUE}Image URLs:${NC}"
  echo "  Registry: ${REGISTRY_IMAGE}"
  echo "  Runner: ${RUNNER_IMAGE}"
  echo "  UI: ${UI_IMAGE}"
else
  echo -e "${YELLOW}💡 Images built locally. To push to ${REGISTRY}, run:${NC}"
  echo "  $0 ${IMAGE_TAG} --push"
  echo ""
  echo -e "${YELLOW}Or manually push each image:${NC}"
  echo "  docker push ${REGISTRY_IMAGE}"
  echo "  docker push ${RUNNER_IMAGE}"
  echo "  docker push ${UI_IMAGE}"
fi

echo ""
echo -e "${BLUE}✅ Build complete!${NC}"


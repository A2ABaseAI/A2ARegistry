# Building and Publishing Docker Images

This guide explains how to build and publish Docker images for the A2A Registry components to GitHub Container Registry (ghcr.io).

## Prerequisites

1. Docker installed and running
2. GitHub account with access to the repository
3. GitHub Personal Access Token (PAT) with `write:packages` permission

## GitHub Container Registry Login

First, login to GitHub Container Registry:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Or interactively:

```bash
docker login ghcr.io
# Username: YOUR_GITHUB_USERNAME
# Password: YOUR_GITHUB_PERSONAL_ACCESS_TOKEN
```

To create a GitHub Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with `write:packages` scope
3. Copy the token and use it as the password when logging in

## Building Images

### Build All Images (without pushing)

```bash
cd k8s
./build-images.sh
```

This will build all three images:
- `ghcr.io/a2areg/a2a-registry/registry:latest`
- `ghcr.io/a2areg/a2a-registry/runner:latest`
- `ghcr.io/a2areg/a2a-registry/ui:latest`

### Build with Custom Tag

```bash
./build-images.sh v1.0.0
```

### Build and Push All Images

```bash
./build-images.sh latest --push
```

Or with a custom tag:

```bash
./build-images.sh v1.0.0 --push
```

### Build Individual Images

If you only want to build/push a specific image:

**Registry:**
```bash
docker build -f registry/Dockerfile.registry -t ghcr.io/a2areg/a2a-registry/registry:latest .
docker push ghcr.io/a2areg/a2a-registry/registry:latest
```

**Runner:**
```bash
docker build -f runner/Dockerfile.runner -t ghcr.io/a2areg/a2a-registry/runner:latest .
docker push ghcr.io/a2areg/a2a-registry/runner:latest
```

**UI:**
```bash
cd ui
docker build -f Dockerfile -t ghcr.io/a2areg/a2a-registry/ui:latest .
docker push ghcr.io/a2areg/a2a-registry/ui:latest
cd ..
```

## Image URLs

After building and pushing, your images will be available at:

- **Registry**: `ghcr.io/a2areg/a2a-registry/registry:latest`
- **Runner**: `ghcr.io/a2areg/a2a-registry/runner:latest`
- **UI**: `ghcr.io/a2areg/a2a-registry/ui:latest`

## Viewing Images on GitHub

1. Go to your GitHub repository: `https://github.com/A2AReg/a2a-registry`
2. Click on "Packages" in the right sidebar
3. You'll see all published container images

## Updating Kubernetes Deployments

The Kubernetes deployment files are already configured to use the GitHub Container Registry images:

- `registry-deployment.yaml`: `ghcr.io/a2areg/a2a-registry/registry:latest`
- `runner-deployment.yaml`: `ghcr.io/a2areg/a2a-registry/runner:latest`
- `ui-deployment.yaml`: `ghcr.io/a2areg/a2a-registry/ui:latest`

After pushing new images, Kubernetes will automatically pull the new versions if `imagePullPolicy: Always` is set (which it is).

## Making Images Public

By default, GitHub Container Registry images are private. To make them public:

1. Go to your GitHub repository
2. Click on "Packages" in the sidebar
3. Click on the package you want to make public
4. Go to "Package settings"
5. Scroll down and click "Change visibility"
6. Select "Public"

## Troubleshooting

### Authentication Errors

If you get authentication errors:
- Make sure you're logged in: `docker login ghcr.io`
- Verify your token has `write:packages` permission
- Check that your GitHub username matches the repository owner

### Permission Denied

If you get permission denied errors:
- Make sure the image name matches: `ghcr.io/a2areg/a2a-registry/...`
- Verify you have write access to the repository
- Try pulling a public image first to test: `docker pull ghcr.io/a2areg/a2a-registry/registry:latest`

### Build Failures

If builds fail:
- Make sure all dependencies are available
- Check that Docker has enough resources allocated
- Verify the Dockerfiles are in the correct locations

## CI/CD Integration

You can also set up GitHub Actions to automatically build and push images on each commit or release. See `.github/workflows/` for example workflows.


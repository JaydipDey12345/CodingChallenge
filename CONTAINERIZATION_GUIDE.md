# Docker Containerization - Quick Start

## Files Created

### 1. **Dockerfile** (Multi-stage Build)
- **Stage 1 (Builder)**: Compiles Python dependencies in isolation using `python:3.9-slim`
- **Stage 2 (Runtime)**: Uses `arjones/pyspark:2.4.5` base image with copied dependencies
- **Benefits**: Reduced image size, faster builds with cached layers, security isolation

### 2. **docker-compose.yml** (v3.9 - Best Practices)
- Version 3.9 (upgraded from v1 for modern features)
- **Health Checks**: All services have startup verification
- **Resource Limits**: CPU and memory constraints to prevent resource exhaustion
- **Dependency Ordering**: Services start only when dependencies are healthy
- **Logging**: Configured with rotation to prevent disk space issues
- **Named Volumes**: Explicit volume management
- **Network**: Custom bridge network for inter-service communication

### 3. **.dockerignore**
- Excludes unnecessary files from build context
- Speeds up builds and reduces image size

### 4. **requirements.txt** (Optional)
- Preconfigured with common data engineering libraries
- Modify as needed for your project

## Running Your Project

### Start All Services
```bash
docker compose up -d --pull always
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f jupyter
docker compose logs -f master
```

### Access Services
- **Jupyter Notebook**: http://localhost:8888
- **Spark Master UI**: http://localhost:8080
- **Spark Worker 1 UI**: http://localhost:8081
- **Spark Worker 2 UI**: http://localhost:8082
- **Documentation**: http://localhost

## Key Improvements Over Original

| Feature | Original | Updated |
|---------|----------|---------|
| Version | v1 | v3.9 |
| Health Checks | ❌ | ✅ All services |
| Resource Limits | ❌ | ✅ CPU & Memory |
| Dependency Conditions | ❌ | ✅ Healthy status |
| Volume Types | Basic | Explicit named volumes |
| Logging | Default | JSON driver with rotation |
| Image Optimization | Single-stage | Multi-stage build |
| Base Image | — | Pinned to 3.9-slim |

## Development Workflow

### Code Changes with Hot Reload
All code volumes are mounted as read-write (`rw`):
```yaml
volumes:
  - ./code:/app:rw
  - ./jupyter/notebook:/notebook:rw
```

Changes made locally appear immediately in containers.

### Adding Dependencies
1. Update `requirements.txt`
2. Rebuild: `docker build -t pyspark-assessment:latest .`
3. Restart: `docker compose up -d jupyter`

## Production Readiness

For production deployments:
- Increase `max-size` and `max-file` in logging config
- Consider using Docker Swarm or Kubernetes
- Use environment-specific compose files: `docker-compose.prod.yml`
- Implement CI/CD with Docker Build Cloud (https://docs.docker.com/build-cloud/)

## Resources

- Docker Compose: https://docs.docker.com/compose/
- Dockerfile Best Practices: https://docs.docker.com/reference/dockerfile/
- Build Optimization: https://docs.docker.com/build/cache/

# CI/CD Pipeline

## Overview
Automated pipeline using Jenkins that builds, tests, and deploys the social media backend application.

## Pipeline Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Commit    │───▶│   Jenkins   │───▶│   Testing   │───▶│   Deploy    │
│   to Git    │    │   Trigger   │    │   & Build   │    │   to Prod   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ Code Quality│
                   │   Checks    │
                   └─────────────┘
```

## Pipeline Stages

### 1. Setup Python
- Creates virtual environment
- Installs dependencies from `requirements.txt`
- Runs initial test suite

### 2. Build
- Starts test PostgreSQL and Redis containers
- Runs database migrations
- Builds Docker image with version tag
- Prepares application for deployment

### 3. Test
- Runs Django test suite with verbosity
- Tests GraphQL endpoints
- Validates database connections
- Ensures Redis connectivity

### 4. Package
- Tags Docker image for deployment
- Creates deployment package with configs
- Archives build artifacts
- Generates version file

### 5. Deploy
- Stops existing application containers
- Deploys new version with environment variables
- Performs basic health check
- Validates service availability

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `POSTGRES_DB` | Database name | `social_media_feed_db` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `your_password` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `NEW_VERSION` | Build version | `1.3.0` |

## Required Services

### Development
- PostgreSQL 13+
- Redis 6+
- Python 3.8+
- Docker

### Jenkins Setup
- Docker plugin
- Pipeline plugin
- Git integration

## Pipeline Configuration

### Triggers
- Automatic on Git push to main branch
- Manual trigger available

### Build Artifacts
- Docker images tagged with version
- Deployment configurations
- Build logs and test results

### Health Checks
- Database connectivity test
- Redis connection validation
- GraphQL endpoint verification
- Admin panel accessibility

## Deployment Process

1. **Build Phase**: Creates Docker image with all dependencies
2. **Test Phase**: Validates functionality with test database
3. **Package Phase**: Prepares deployment artifacts
4. **Deploy Phase**: Replaces running container with new version

## Cleanup
- Removes test containers after build
- Cleans up virtual environment
- Removes temporary files

## Monitoring

### Success Criteria
- All tests pass
- Docker image builds successfully
- Health checks return 200 status
- Application starts within 30 seconds

### Failure Handling
- Pipeline stops on any stage failure
- Test containers are cleaned up
- Build artifacts are preserved for debugging
- Notification sent on failure

## Quick Commands

### Manual Build
```bash
# Run pipeline manually
Jenkins > Build with Parameters > Start Build
```

### Check Deployment
```bash
# Verify application is running
curl http://localhost:8000/admin/

# Check container status
docker ps | grep social-media-app
```

### Rollback
```bash
# Stop current deployment
docker stop social-media-app

# Start previous version
docker run -d --name social-media-app -p 8000:8000 social-media-backend:previous-version
```

## Integration Points

### Payment System
- Chapa payment gateway integration
- Test and live API keys configured
- Sandbox testing in pipeline

### Email Service
- SMTP configuration for notifications
- Email testing in pipeline
- Gmail integration setup

### Database
- PostgreSQL with custom indexing
- Migration testing included
- Data seeding for tests

## Build Duration
- **Setup**: ~2 minutes
- **Build**: ~3 minutes  
- **Test**: ~2 minutes
- **Package**: ~1 minute
- **Deploy**: ~2 minutes
- **Total**: ~10 minutes

## Troubleshooting

### Common Issues
- **Database connection failed**: Check PostgreSQL container status
- **Redis not available**: Verify Redis container is running
- **Tests failing**: Check test database has proper schema
- **Docker build failed**: Verify Dockerfile syntax and dependencies

### Debug Commands
```bash
# Check container logs
docker logs test_postgres
docker logs test_redis

# Verify database
docker exec -it test_postgres psql -U postgres -d test_social_media_db -c '\dt'

# Test Redis
docker exec -it test_redis redis-cli ping
```
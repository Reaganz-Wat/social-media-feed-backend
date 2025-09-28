# Social Media Feed Backend

A production-ready Django-powered backend for a social media feed application with GraphQL API, real-time subscriptions, and advanced database optimization. Built with scalability, performance, and maintainability as core principles.

## Technical Stack

| Technology | Purpose | Implementation |
|------------|---------|----------------|
| **Django 4.x** | Web framework | RESTful APIs and GraphQL endpoints |
| **GraphQL** | API layer | Queries, mutations, and real-time subscriptions |
| **PostgreSQL** | Primary database | Optimized with custom indexing strategy |
| **Redis** | Cache & message broker | Celery task queue and session storage |
| **Celery** | Async task processing | Background jobs and notifications |
| **WebSockets** | Real-time features | Live likes, comments, and feed updates |
| **JWT** | Authentication | Secure token-based auth |
| **Docker** | Containerization | Development and deployment |

## Features

### Core Functionality
- **User Management**: Registration, authentication, profiles with JWT
- **Content System**: Posts with media support, CRUD operations
- **Engagement**: Real-time likes, comments with threading
- **Social Graph**: Follow/unfollow relationships, friend requests
- **Feed Algorithm**: Personalized feeds with trending content
- **Messaging**: Private messaging system

### Technical Features
- **GraphQL API**: Efficient queries with real-time subscriptions
- **Database Optimization**: Custom indexing for 99% performance improvement
- **Async Processing**: Background tasks with Celery
- **Real-time Updates**: WebSocket subscriptions for live interactions
- **Comprehensive Testing**: Unit and integration tests
- **Production Ready**: Docker, environment configuration, monitoring

## Quick Start

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/Reaganz-Wat/social-media-feed-backend.git
cd social-media-feed-backend
```

2. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

4. **Database Setup**
```bash
# Create database
createdb social_media_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed sample data (optional)
python manage.py seed
```

5. **Start Services**

**Terminal 1 - Main Application (ASGI Server)**
```bash
uvicorn social_media_feed_backend.asgi:application --reload --port 8000
```

**Terminal 2 - Celery Worker**
```bash
celery -A social_media_feed_backend worker -l info
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **GraphQL Playground** | http://localhost:8000/graphql | Interactive API explorer |
| **GraphQL Endpoint** | http://localhost:8000/graphql | API endpoint for client apps |
| **WebSocket Subscriptions** | ws://127.0.0.1:8000/graphql-ws/ | Real-time subscriptions |
| **Admin Panel** | http://localhost:8000/admin | Django admin interface |


### Performance Optimization

The application implements advanced database optimization:

- **Custom Indexing Strategy**: 99% performance improvement on feed queries
- **Query Optimization**: Efficient GraphQL resolvers with minimal N+1 queries
- **Caching Layer**: Redis caching for frequently accessed data
- **Async Processing**: Background tasks for notifications and analytics

## Testing

### Run Test Suite
```bash
# All tests
python manage.py test

# Specific app tests
python manage.py test social_media_feed_app

# Coverage report
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Categories
- **Unit Tests**: Model methods, utility functions
- **Integration Tests**: API endpoints, GraphQL resolvers
- **Performance Tests**: Database query optimization
- **WebSocket Tests**: Real-time subscription functionality

## Docker Deployment

### Development
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web
```

## Repository Structure

```text
social_media_feed_backend/
│
├── docs/                                    # 📚 Comprehensive documentation
│   ├── 00_PROJECT_OVERVIEW.md
│   ├── 01_REQUIREMENTS.md
│   ├── 02_ARCHITECTURE.md
│   ├── 03_DEPLOYMENTS.md
│   ├── 04_UNIT_TEST.md
│   └── database/
│       ├── 01_ER_DIAGRAM.md
│       ├── 02_SCHEMA.md
│       ├── 03_INDEXING_STRATEGY.md
│       └── 04_SEEDING_AND_MIGRATIONS.md
│
├── social_media_feed_backend/               # 🐍 Django project configuration
│   ├── __init__.py
│   ├── asgi.py                             # ASGI config for WebSockets
│   ├── celery.py                           # Celery configuration
│   ├── settings.py                         # Environment-based settings
│   ├── urls.py                             # URL routing
│   └── wsgi.py                             # WSGI config for production
│
├── social_media_feed_app/                   # 📦 Main application logic
│   ├── management/commands/
│   │   └── seed.py                         # Database seeding utility
│   ├── migrations/
│   │   ├── 0001_initial.py                 # Initial schema
│   │   └── 0002_add_database_indexes.py    # Performance optimization
│   ├── schema/                             # GraphQL implementation
│   │   ├── __init__.py
│   │   ├── inputs.py                       # GraphQL input types
│   │   ├── mutations.py                    # GraphQL mutations
│   │   ├── queries.py                      # GraphQL queries
│   │   ├── schema.py                       # Schema composition
│   │   ├── subscriptions.py                # Real-time subscriptions
│   │   └── types.py                        # GraphQL types
│   ├── __init__.py
│   ├── admin.py                            # Django admin configuration
│   ├── apps.py                             # App configuration
│   ├── models.py                           # Database models
│   ├── signals.py                          # Django signals
│   ├── tasks.py                            # Celery async tasks
│   ├── tests.py                            # Test suite
│   └── views.py                            # Additional view logic
│
├── scripts/                                 # 🔧 Utility scripts
│   └── backup_db.sh                        # Database backup automation
│
├── requirements.txt                         # Python dependencies
├── manage.py                               # Django management
├── .env.example                            # Environment template
├── .gitignore                              # Git ignore rules
├── Jenkinsfile                             # CI/CD pipeline
├── Dockerfile                              # Container definition
├── docker-compose.yml                      # Development environment
└── README.md                               # This documentation
```

## Development Workflow

### Code Quality
- **Testing**: Comprehensive test coverage
- **Documentation**: Inline docstrings and API docs

### Database Migrations
```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Custom data migration
python manage.py makemigrations --empty app_name
```

## Monitoring & Maintenance

### Performance Monitoring
```bash
# Database query analysis
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)

# Index usage monitoring
python manage.py shell_plus
# Run SQL queries from docs/database/03_INDEXING_STRATEGY.md
```

### Health Checks
```bash
# Redis connectivity
redis-cli ping
```

## Architecture Highlights

### Scalability Features
- **Database Optimization**: Advanced indexing for millions of users
- **Async Processing**: Non-blocking background tasks
- **Caching Strategy**: Multi-layer caching with Redis

### Security Implementation
- **JWT Authentication**: Secure token-based auth
- **SQL Injection Prevention**: Django ORM protection
- **Rate Limiting**: API endpoint protection

### Real-time Capabilities
- **WebSocket Subscriptions**: Live feed updates
- **Event-driven Architecture**: Real-time notifications
- **Optimistic Updates**: Client-side responsiveness

## Contact

**Developer**: [Watmon Reagan]
**GitHub**: [https://github.com/Reaganz-Wat](https://github.com/Reaganz-Wat)

---
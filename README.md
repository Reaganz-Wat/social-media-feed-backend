# Social Media Feed Backend

A Django-powered backend for a social media feed application.  
It provides APIs for user management, posts, likes, comments, following relationships, and personalized feeds.  
The project is designed with scalability, modularity, and clean documentation in mind.

---

## 🚀 Features
- User authentication & profiles (JWT-based)
- CRUD for posts (create, update, delete, view)
- Like & comment on posts
- Follow/unfollow users
- Generate personalized feeds
- REST API built with Django REST Framework
- PostgreSQL as primary database with indexing strategy
- Dockerized for easy deployment

---

## 📂 Repository Structure

### 🔹 Codebase
```text
social_feed_backend/
│
├── docs/                          # 📚 Documentation (see below)
│
├── social_feed/                   # 🐍 Main Django project folder
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # Base settings
│   ├── urls.py
│   └── wsgi.py
│
├── apps/                          # 📦 Django apps (modularized)
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── ...
│   │
│   ├── posts/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   ├── feed/
│   │   ├── services.py             # feed generation logic
│   │   ├── views.py
│   │   └── ...
│   │
│   └── notifications/
│       ├── models.py
│       └── ...
│
├── config/                        # ⚙️ Config & infra stuff
│   ├── settings/                   # Split settings by env
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── prod.py
│   │   └── test.py
│   ├── logging.yaml
│   └── gunicorn.conf.py
│
├── tests/                         # ✅ Extra test directory if needed
│
├── scripts/                       # 🔧 Utility scripts
│   ├── seed_data.py
│   └── backup_db.sh
│
├── requirements.txt                # or pyproject.toml (if poetry)
├── manage.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Docs
```text
/docs
│
├── 00_PROJECT_OVERVIEW.md
├── 01_REQUIREMENTS.md
├── 02_ARCHITECTURE.md
│
├── database/
│   ├── 01_ER_DIAGRAM.md
│   ├── 02_SCHEMA.md
│   ├── 03_INDEXING_STRATEGY.md
│   └── 04_SEEDING_AND_MIGRATIONS.md
│
├── backend/
│   ├── 01_DJANGO_SETUP.md
│   ├── 02_APPS_STRUCTURE.md
│   ├── 03_MODELS.md
│   ├── 04_SERIALIZERS.md
│   ├── 05_VIEWS_AND_ENDPOINTS.md
│   ├── 06_PERMISSIONS_AND_AUTH.md
│   └── 07_TESTING.md
│
├── infra/
│   ├── 01_SETTINGS.md
│   ├── 02_ENVIRONMENT.md
│   ├── 03_DEPLOYMENT.md
│   └── 04_LOGGING_MONITORING.md
│
└── README.md
```
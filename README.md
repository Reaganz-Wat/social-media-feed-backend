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
social_media_feed_backend/
│
├── docs/                          # 📚 Documentation (see below)
│
├── social_media_feed_backend/                   # 🐍 Main Django project folder
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # Base settings
│   ├── urls.py
│   └── wsgi.py
│
├── social_media_feed_app/                          # 📦 Django apps (modularized)
│   ├── management/
│   │   └──commands/
|   |      └──seed.py
|   |
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 00001_initial.py
|   |
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── inputs.py
│   │   ├── mutations.py
│   │   ├── queries.py
|   |   ├── schema.py
│   │   └── types.py
|   |
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   └── views.py
│
├── venv/                          # virtual environment
│
├── scripts/                       # 🔧 Utility scripts
│   └── backup_db.sh
│
├── requirements.txt                # or pyproject.toml (if poetry)
├── manage.py
├── .env.example
├── .gitignore
├── .Jenkinsfile
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
└── README.md
```
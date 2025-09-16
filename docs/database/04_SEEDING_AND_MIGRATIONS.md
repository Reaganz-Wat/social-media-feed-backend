# Database Seeding

Database seeding is the process of **populating the database with sample data** for testing and development purposes.
It allows developers to test CRUD operations, view realistic interactions, and simulate real-world scenarios without manually inserting data.

[TOC]

---

## Installing & Running

1. Ensure your virtual environment is active:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

## What It Seeds
- Users (5 default)
- Posts, Comments, Likes...
- Messages, Follows, Interactions

## Usage Examples
```bash
python manage.py seed
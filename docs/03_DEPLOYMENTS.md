# Deployments

This document explains the deployment architecture that has been implemented for our Django + GraphQL app using PostgreSQL, Redis, and Celery on free-tier services.

## Architecture Overview

* **PythonAnywhere → Django + GraphQL**

  * Hosts the Django web application and GraphQL API.
  * Always-on (no cold starts) on free tier.
  * Handles HTTP requests from users.

* **Supabase → Postgres**

  * Managed PostgreSQL database.
  * Stores all persistent data for the Django app.
  * Provides secure and reliable free-tier database service.

* **Redis Cloud → broker**

  * Acts as the message broker for Celery.
  * Handles task queues for background processing.
  * Also used as a caching layer for Django.

* **Render → Celery worker**

  * Runs background worker processes for Celery tasks.
  * Connects to the Redis broker and Postgres database.
  * Runs independently of the Django web app.

## Deployment Notes

1. **Django + GraphQL (PythonAnywhere)**

   * The Git repository has been linked.
   * Environment variables set:

     * `DJANGO_SETTINGS_MODULE=social_media_feed_backend.settings`
     * `DATABASE_URL` → Supabase connection string
     * `REDIS_URL` → Redis Cloud URL
   * Gunicorn/Uvicorn is used to serve the web app.

2. **Postgres (Supabase)**

   * Free tier provides ~500 MB storage.
   * `DATABASE_URL` is used in Django settings.

3. **Redis Cloud**

   * Free tier provides ~30 MB memory.
   * `REDIS_URL` environment variable is used in Django settings and Celery config.

4. **Celery Worker (Render)**

   * Background worker service created on Render.
   * Celery started with:

     ```bash
     celery -A social_media_feed_backend worker -l info
     ```
   * Worker has access to environment variables:

     * `DJANGO_SETTINGS_MODULE`
     * `DATABASE_URL`
     * `REDIS_URL`
   * Executes tasks enqueued by the Django web app.

## Summary

This multi-provider deployment allows the Django + GraphQL app with background task processing to run fully on free-tier services. Each component is hosted in a way that suits its role:

* PythonAnywhere for always-on web app.
* Supabase for database.
* Redis Cloud for task broker.
* Render for background Celery workers.
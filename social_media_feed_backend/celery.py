import os
from celery import Celery

# Celery is a standalone process (not started via manage.py),
# so it doesn't know where Django's settings live by default.
# This line points Celery to Django’s settings module.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_feed_backend.settings')

# Create the main Celery application instance.
# The name "social_media_feed_backend" is just an identifier,
# usually the same as your Django project name.
app = Celery("social_media_feed_backend")

# Load Celery configuration from Django’s settings file.
# It will only pick up values that start with "CELERY_"
# (e.g., CELERY_BROKER_URL, CELERY_RESULT_BACKEND).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Tell Celery to automatically discover tasks in all Django apps
# listed in INSTALLED_APPS by looking for a "tasks.py" file.
app.autodiscover_tasks()
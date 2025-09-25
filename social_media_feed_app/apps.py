from django.apps import AppConfig


class SocialMediaFeedAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_media_feed_app'

    def ready(self):
        # Import signals to ensure they're registered
        import social_media_feed_app.signals
"""
ASGI config for social_media_feed_backend project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
import channels_graphql_ws

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media_feed_backend.settings")
django_asgi_app = get_asgi_application()

# ✅ Import the FULL schema (not just subscriptions)
from social_media_feed_app.schema.schema import schema


# ✅ GraphQL WebSocket consumer
class GraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Custom WebSocket consumer for GraphQL subscriptions."""
    schema = schema

    async def on_connect(self, payload):
        print("✅ WebSocket connected!")

    async def on_disconnect(self, close_code):
        print(f"❌ WebSocket disconnected with code: {close_code}")


# ✅ Application entrypoint
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # WebSocket endpoint for GraphQL subscriptions
            re_path(r"^graphql-ws/$", GraphqlWsConsumer.as_asgi()),
        ])
    ),
})

"""
ASGI config for social_media_feed_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import channels_graphql_ws
from social_media_feed_app.schema.schema import schema

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_feed_backend.settings')

application = get_asgi_application()


# GraphQL WebSocket consumer
class GraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Custom WebSocket consumer for GraphQL subscriptions."""
    
    schema = schema
    
    async def on_connect(self, payload):
        """Handle WebSocket connection."""
        print("WebSocket connected!")
        await self.accept()
    
    async def on_disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        print("WebSocket disconnected!")

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # GraphQL WebSocket endpoint
            channels_graphql_ws.routing.websocket_urlpattern(
                r"^graphql-ws/$",
                consumer=GraphqlWsConsumer,
            ),
        ])
    ),
})
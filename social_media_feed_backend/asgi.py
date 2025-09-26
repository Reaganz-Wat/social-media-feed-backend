# """
# ASGI config for social_media_feed_backend project.
# """
# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import channels_graphql_ws

# # ✅ Import the FULL schema, not just subscriptions
# from social_media_feed_app.schema.schema import schema

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_feed_backend.settings')
# django_asgi_app = get_asgi_application()

# # GraphQL WebSocket consumer
# class GraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
#     """Custom WebSocket consumer for GraphQL subscriptions."""
#     # ✅ Use the full GraphQL schema here
#     schema = schema
    
#     async def on_connect(self, payload):
#         """Handle WebSocket connection."""
#         print("WebSocket connected!")
#         await self.accept()
    
#     async def on_disconnect(self, close_code):
#         """Handle WebSocket disconnection."""
#         print(f"WebSocket disconnected with code: {close_code}")

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             # GraphQL WebSocket endpoint
#             channels_graphql_ws.routing.websocket_urlpattern(
#                 r"^graphql-ws/$",
#                 consumer=GraphqlWsConsumer,
#             ),
#         ])
#     ),
# })




"""
ASGI config for social_media_feed_backend project.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from django.urls import path
import channels_graphql_ws

# ✅ Import the FULL schema, not just subscriptions
from social_media_feed_app.schema.schema import schema

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_feed_backend.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# GraphQL WebSocket consumer
class GraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Custom WebSocket consumer for GraphQL subscriptions."""
    # ✅ Use the full GraphQL schema here
    schema = schema
    
    async def on_connect(self, payload):
        """Handle WebSocket connection."""
        print("WebSocket connected!")
        print(f"Connection payload: {payload}")
        await self.accept()
    
    async def on_disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        print(f"WebSocket disconnected with code: {close_code}")

# ✅ Create WebSocket URL patterns
websocket_urlpatterns = [
    path("graphql-ws/", GraphqlWsConsumer.as_asgi()),
]

# ✅ Main ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
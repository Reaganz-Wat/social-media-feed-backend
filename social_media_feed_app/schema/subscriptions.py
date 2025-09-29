import graphene
import channels_graphql_ws
from .types import PostType, CustomUserType, CommentType

class PostCreatedSubscription(channels_graphql_ws.Subscription):
    """Subscription for new posts."""
    
    # Define the output field
    post = graphene.Field(PostType)
    
    class Arguments:
        # Optional: filter by user ID
        user_id = graphene.ID()
    
    @staticmethod
    def subscribe(root, info, user_id=None):
        """Subscribe to post creation events."""
        # Return the subscription group name(s)
        if user_id:
            return [f"post_created_by_{user_id}"]
        return ["post_created"]
    
    @staticmethod
    def publish(payload, info, user_id=None):
        """Called when triggering the subscription."""
        # payload is the post object from the broadcast
        return PostCreatedSubscription(post=payload)

class PostLikedSubscription(channels_graphql_ws.Subscription):
    """Subscription for post likes."""
    
    post = graphene.Field(PostType)
    user = graphene.Field(CustomUserType)
    likes_count = graphene.Int()
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    @staticmethod
    def subscribe(root, info, post_id):
        """Subscribe to like events for a specific post."""
        return [f"post_liked_{post_id}"]
    
    @staticmethod
    def publish(payload, info, post_id):
        """Called when publishing like events."""
        # payload should be a dict with post, user, likes_count
        return PostLikedSubscription(
            post=payload.get('post'),
            user=payload.get('user'),
            likes_count=payload.get('likes_count', 0)
        )

class CommentCreatedSubscription(channels_graphql_ws.Subscription):
    """Subscription for new comments."""
    
    comment = graphene.Field(CommentType)
    post = graphene.Field(PostType)
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    @staticmethod
    def subscribe(root, info, post_id):
        """Subscribe to comment events for a specific post."""
        return [f"comment_created_{post_id}"]
    
    @staticmethod
    def publish(payload, info, post_id):
        """Called when publishing comment events."""
        # payload is the comment object
        return CommentCreatedSubscription(
            comment=payload,
            post=payload.post if hasattr(payload, 'post') else None
        )

class Subscription(graphene.ObjectType):
    """Main subscription class that combines all subscriptions."""
    post_created = PostCreatedSubscription.Field()
    post_liked = PostLikedSubscription.Field()
    comment_created = CommentCreatedSubscription.Field()
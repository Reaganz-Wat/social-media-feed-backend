import graphene
from .types import PostCreatedType, PostLikedType, CommentCreatedType
import channels_graphql_ws

class PostCreatedSubscription(channels_graphql_ws.Subscription):
    """Subscription for new posts."""
    
    class Arguments:
        # Optional: filter by user ID
        user_id = graphene.ID()
    
    class Meta:
        # Subscription payload type
        serializer = PostCreatedType
        
    def subscribe(self, info, user_id=None):
        """Subscribe to post creation events."""
        # Return the subscription group name
        if user_id:
            return [f"post_created_by_{user_id}"]
        return ["post_created"]
    
    def publish(self, info, user_id=None):
        """Called when triggering the subscription."""
        # This method defines what data is sent to subscribers
        return PostCreatedType(post=self)

class PostLikedSubscription(channels_graphql_ws.Subscription):
    """Subscription for post likes."""
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    class Meta:
        serializer = PostLikedType
        
    def subscribe(self, info, post_id):
        """Subscribe to like events for a specific post."""
        return [f"post_liked_{post_id}"]
    
    def publish(self, info, post_id):
        """Called when publishing like events."""
        return PostLikedType(
            post=self.post,
            user=self.user,
            likes_count=self.post.likes.count()
        )

class CommentCreatedSubscription(channels_graphql_ws.Subscription):
    """Subscription for new comments."""
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    class Meta:
        serializer = CommentCreatedType
        
    def subscribe(self, info, post_id):
        """Subscribe to comment events for a specific post."""
        return [f"comment_created_{post_id}"]
    
    def publish(self, info, post_id):
        """Called when publishing comment events."""
        return CommentCreatedType(
            comment=self,
            post=self.post
        )
        

class Subscription(graphene.ObjectType):
    post_created = PostCreatedSubscription.Field()
    post_liked = PostLikedSubscription.Field()
    comment_created = CommentCreatedSubscription.Field()
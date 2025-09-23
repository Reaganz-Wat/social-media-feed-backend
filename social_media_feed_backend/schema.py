import graphene
from graphene_django import DjangoObjectType
from social_media_feed_app.models import (
    Comment, 
    CommentLike, 
    CustomUser, 
    Post, 
    PostLike, 
    Share, 
    Follow, 
    Friendship, 
    Message, 
    Interaction
)
from django.utils import timezone
from django.db.models import Count, Q, F
from datetime import timedelta

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = "__all__"
        
class PostType(DjangoObjectType):
    likes_count = graphene.Int()
    comment_count = graphene.Int()
    share_count = graphene.Int()
    
    class Meta:
        model = Post
        fields = "__all__"
        
    def resolve_likes_count(self, info):
        return self.likes.count()
    
    def resolve_comment_count(self, info):
        return self.comments.filter(is_deleted=False).count()
    
    def resolve_share_count(self, info):
        return self.shares.count()
        
class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"
        
class CommentLikeType(DjangoObjectType):
    class Meta:
        model = CommentLike
        fields = "__all__"
        
class PostLikeType(DjangoObjectType):
    class Meta:
        model = PostLike
        fields = "__all__"
        
class ShareType(DjangoObjectType):
    class Meta:
        model = Share
        fields = "__all__"
        
class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = "__all__"
        
class FriendshipType(DjangoObjectType):
    class Meta:
        model = Friendship
        fields = "__all__"
        
class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = "__all__"
        
class InteractionType(DjangoObjectType):
    class Meta:
        model = Interaction
        fields = "__all__"

class UserStatsType(graphene.ObjectType):
    total_posts = graphene.Int()
    total_likes = graphene.Int()
    total_comments = graphene.Int()
    total_shares = graphene.Int()
    followers_count = graphene.Int()
    following_count = graphene.Int()
    engagement_rate = graphene.Float()
    top_performing_post = graphene.Field(PostType)

class Query(graphene.ObjectType):
    all_users = graphene.List(CustomUserType)
    all_posts = graphene.List(PostType, limit=graphene.Int(default_value=10), offset=graphene.Int(default_value=0), user_id=graphene.ID())
    all_comments = graphene.List(CommentType)
    all_comment_likes = graphene.List(CommentLikeType)
    all_post_likes = graphene.List(PostLikeType)
    all_shares = graphene.List(ShareType)
    all_follows = graphene.List(FollowType)
    all_friends = graphene.List(FriendshipType)
    all_messages = graphene.List(MessageType)
    all_interactions = graphene.List(InteractionType)
    post_by_id = graphene.Field(PostType, id=graphene.ID(required=True))
    post_comments = graphene.List(CommentType, id=graphene.ID(required=True))
    trending_posts = graphene.List(PostType, limit=graphene.Int(default_value=12), hours=graphene.Int(default_value=24))
    user_by_id = graphene.Field(CustomUserType, id=graphene.ID(required=True))
    user_stats = graphene.Field(UserStatsType, id=graphene.ID(required=True))
    
    user_feed = graphene.List(
        PostType,
        limit=graphene.Int(default_value=10),
        offset=graphene.Int(default_value=0)
    )
    
    def resolve_all_users(root, info):
        return CustomUser.objects.all()
    
    def resolve_all_posts(root, info, limit=10, offset=0, user_id=None):
        # return Post.objects.all()
        
        queryset = Post.objects.filter(is_deleted=False).select_related('user').prefetch_related('likes', 'comments', 'shares')
        
        # Filter by user if specified
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        return queryset[offset:offset + limit]
    
    def resolve_post_by_id(self, info, id):
        """
        Get a single post by ID with all related data
        """
        try:
            return Post.objects.select_related('user').prefetch_related(
                'comments__user',
                'likes__user',
                'shares__user'
            ).get(id=id, is_deleted=False)
        except Post.DoesNotExist:
            return None
        
    
    def resolve_user_feed(self, info, limit=10, offset=0):
        """
        Personalized feed showing posts from followed users
        Note: This requires authentication - you'll need to implement JWT auth
        """
        # Get current user from context (requires authentication middleware)
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        # Get IDs of users that current user follows
        following_users = Follow.objects.filter(follower=user).values_list('followee_id', flat=True)
        
        # Include current user's posts too
        user_ids = list(following_users) + [user.id]
        
        queryset = Post.objects.filter(
            user_id__in=user_ids,
            is_deleted=False
        ).select_related('user').prefetch_related('likes', 'comments', 'shares')
        
        queryset = queryset.order_by('-created_at')
        return queryset[offset:offset + limit]
    
    
    def resolve_post_comments(root, info, post_id=0):
        
        """This post comments returns a list of
        comments for a post given the id of the post,and it returns 
        the comments for that post"""
        
        return Comment.objects.filter(
            post_id=post_id,
            parent_comment=None,  # Only top-level comments
            is_deleted=False
        ).select_related('user').prefetch_related('replies', 'likes').order_by('created_at')
    
    
    def resolve_trending_posts(self, info, limit=10, hours=24):
        """
        Get trending posts based on engagement in the last X hours
        """
        time_threshold = timezone.now() - timedelta(hours=hours)
        
        # Get posts with engagement counts from the specified time period
        queryset = Post.objects.filter(
            created_at__gte=time_threshold,
            is_deleted=False
        ).annotate(
            recent_likes=Count('likes', filter=Q(likes__created_at__gte=time_threshold)),
            recent_comments=Count('comments', filter=Q(comments__created_at__gte=time_threshold, comments__is_deleted=False)),
            recent_shares=Count('shares', filter=Q(shares__created_at__gte=time_threshold)),
            # Calculate engagement score
            engagement_score=F('recent_likes') + F('recent_comments') * 2 + F('recent_shares') * 3
        ).select_related('user').prefetch_related('likes', 'comments', 'shares')
        
        return queryset.order_by('-engagement_score')[:limit]
    
    def resolve_user_by_id(root, info, id):
        """This query returns the user information by the id"""
        
        try:
            return CustomUser.objects.prefetch_related('posts',
                'followers',
                'following').get(id=id)
        except CustomUser.DoesNotExist:
            return None
        
    def resolve_user_stats(self, info, id):
            """
            Get comprehensive user statistics
            """
            try:
                user = CustomUser.objects.get(id=id)
            except CustomUser.DoesNotExist:
                return None
            
            # Calculate stats
            total_posts = user.posts.filter(is_deleted=False).count()
            total_likes = PostLike.objects.filter(post__user=user).count()
            total_comments = Comment.objects.filter(post__user=user, is_deleted=False).count()
            total_shares = Share.objects.filter(post__user=user).count()
            followers_count = user.followers.count()
            following_count = user.following.count()
            
            # Calculate engagement rate
            total_engagement = total_likes + total_comments + total_shares
            engagement_rate = (total_engagement / max(total_posts, 1)) if total_posts > 0 else 0
            
            # Get top performing post
            top_post = user.posts.filter(is_deleted=False).annotate(
                engagement=Count('likes') + Count('comments') + Count('shares')
            ).order_by('-engagement').first()
            
            return UserStatsType(
                total_posts=total_posts,
                total_likes=total_likes,
                total_comments=total_comments,
                total_shares=total_shares,
                followers_count=followers_count,
                following_count=following_count,
                engagement_rate=engagement_rate,
                top_performing_post=top_post
            )
        
    
    def resolve_all_comments(root, info):
        return Comment.objects.all()
    
    def resolve_all_comment_likes(root, info):
        return CommentLike.objects.all()
    
    def resolve_all_post_likes(root, info):
        return PostLike.objects.all()
    
    def resolve_all_shares(root, info):
        return Share.objects.all()
    
    def resolve_all_follows(root, info):
        return Follow.objects.all()
    
    def resolve_all_friends(root, info):
        return Friendship.objects.all()
    
    def resolve_all_messages(root, info):
        return Message.objects.all()
    
    def resolve_all_interactions(root, info):
        return Interaction.objects.all()
    

# Mutations
class CreatePost(graphene.Mutation):
    """Mutation to create new post"""
    
    # OUTPUT FIELDS -> This is what the mutations returns
    success = graphene.Boolean()
    message = graphene.String()
    post = graphene.Field(PostType)
    errors = graphene.List(graphene.String)
    
    class Arguments:
        
        # These are the required fields that are needed by the post model
        user_id = graphene.ID(required=True, description="ID of the user who is creating the post")
        content = graphene.String(required=True, description="Post content")
        
        # Optional fields
        title = graphene.String(description="Optional post title")
        media_type = graphene.String(description="Type of media: image, video, audioz, gif")
        
    def mutate(self, info, user_id, content, title=None, media_type=None):
        """
        The mutate method is where all the magic happens!
        
        Parameters:
        - self: The mutation instance
        - info: GraphQL execution info (contains context, user, etc.)
        - user_id, content, title, media_type: The arguments we defined above
        """
        
        try:
            # Step 1: Validate the user exists
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return CreatePost(
                    success=False,
                    message="User nof found",
                    post=None,
                    errors=["Invalid user ID"]
                )
                
            # Validate the content so that it is not empty
            if not content.strip():
                return CreatePost(
                    success=False,
                    message="Content cannot be empty",
                    post=None,
                    errors=["Content is required"]
                )
                
            # Create the post
            post = Post.objects.create(
                user=user,
                title=title,
                content=content.strip(),
                media_type=media_type
            )
            
            # Return success response
            return CreatePost(
                success=True,
                message=f"Post created successfully by {user.username}",
                post=post,
                errors=[]
            )
            
        except Exception as e:
            # Here it handles any unexpected errors
            return CreatePost(
                success=False,
                message="An error occured while creating the post",
                post=None,
                errors=[str(e)]
            )

class Mutation(graphene.ObjectType):
    """This is where you register all your mutations"""
    create_post = CreatePost.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)
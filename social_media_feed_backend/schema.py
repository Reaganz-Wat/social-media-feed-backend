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
import graphql_jwt
from django.forms.models import model_to_dict

# Types ...............
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


# Query ......................
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


# Mutations Inputs .....................
class CreatePostInput(graphene.InputObjectType):
    title = graphene.String()
    content = graphene.String(required=True)
    media_type = graphene.String()

class UpdatePostInput(graphene.InputObjectType):
    title = graphene.String()
    content = graphene.String()
    media_type = graphene.String()

class CreateCommentInput(graphene.InputObjectType):
    post_id = graphene.ID(required=True, description="ID of the comment the post being commented on")
    content = graphene.String(required=True, description="The content for the comment")
    parent_comment_id = graphene.ID()
    
class SharePostInput(graphene.InputObjectType):
    post_id = graphene.ID(required=True)
    caption = graphene.String()


# Murations................

class CreatePost(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    post = graphene.Field(PostType)
    errors = graphene.List(graphene.String)
    
    class Arguments:
        input = CreatePostInput(required=True)
    
    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return CreatePost(
                success=False,
                message="Authentication required",
                errors=["You must be logged in to create a post"]
            )
        
        try:
            if not input.content.strip():
                return CreatePost(
                    success=False,
                    message="Content cannot be empty",
                    errors=["Content is required"]
                )
            
            post = Post.objects.create(
                user=user,
                title=input.title,
                content=input.content.strip(),
                media_type=input.media_type
            )
            
            return CreatePost(
                success=True,
                message=f"Post created successfully",
                post=post,
                errors=[]
            )
            
        except Exception as e:
            return CreatePost(
                success=False,
                message="An error occurred while creating the post",
                errors=[str(e)]
            )

class UpdatePost(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    post = graphene.Field(PostType)
    errors = graphene.List(graphene.String)
    
    class Arguments:
        id = graphene.ID(required=True)
        input = UpdatePostInput(required=True)
    
    def mutate(self, info, id, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdatePost(
                success=False,
                message="Authentication required",
                errors=["You must be logged in"]
            )
        
        try:
            post = Post.objects.get(id=id, user=user, is_deleted=False)
        except Post.DoesNotExist:
            return UpdatePost(
                success=False,
                message="Post not found or you don't have permission",
                errors=["Invalid post ID or insufficient permissions"]
            )
        
        try:
            if input.title is not None:
                post.title = input.title
            if input.content is not None:
                if not input.content.strip():
                    return UpdatePost(
                        success=False,
                        message="Content cannot be empty",
                        errors=["Content is required"]
                    )
                post.content = input.content.strip()
            if input.media_type is not None:
                post.media_type = input.media_type
            
            post.save()
            
            return UpdatePost(
                success=True,
                message="Post updated successfully",
                post=post,
                errors=[]
            )
            
        except Exception as e:
            return UpdatePost(
                success=False,
                message="An error occurred while updating the post",
                errors=[str(e)]
            )

class DeletePost(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    
    class Arguments:
        id = graphene.ID(required=True)
    
    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeletePost(
                success=False,
                message="Authentication required"
            )
        
        try:
            post = Post.objects.get(id=id, user=user, is_deleted=False)
            post.is_deleted = True
            post.save()
            
            return DeletePost(
                success=True,
                message="Post deleted successfully"
            )
            
        except Post.DoesNotExist:
            return DeletePost(
                success=False,
                message="Post not found or you don't have permission"
            )

class LikePost(graphene.Mutation):
    success = graphene.Boolean()
    liked = graphene.Boolean()
    message = graphene.String()
    post = graphene.Field(PostType)
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            return LikePost(
                success=False,
                message="Authentication required"
            )
        
        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            return LikePost(
                success=False,
                message="Post not found"
            )
        
        try:
            # Check if already liked
            like, created = PostLike.objects.get_or_create(
                post=post,
                user=user
            )
            
            if created:
                return LikePost(
                    success=True,
                    liked=True,
                    message="Post liked successfully",
                    post=post
                )
            else:
                return LikePost(
                    success=True,
                    liked=True,
                    message="Post already liked",
                    post=post
                )
                
        except Exception as e:
            return LikePost(
                success=False,
                message=f"An error occurred: {str(e)}"
            )

class UnlikePost(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    post = graphene.Field(PostType)
    
    class Arguments:
        post_id = graphene.ID(required=True)
    
    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            return UnlikePost(
                success=False,
                message="Authentication required"
            )
        
        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            return UnlikePost(
                success=False,
                message="Post not found"
            )
        
        try:
            like = PostLike.objects.get(post=post, user=user)
            like.delete()
            
            return UnlikePost(
                success=True,
                message="Post unliked successfully",
                post=post
            )
            
        except PostLike.DoesNotExist:
            return UnlikePost(
                success=True,
                message="Post was not liked",
                post=post
            )

class CreateComment(graphene.Mutation):
    """Mutation to create a new comment on a post"""
    
    # OUTPUT FIELDS -> This is what the mutations returns
    success = graphene.Boolean()
    message = graphene.String()
    comment = graphene.Field(CommentType)
    errors = graphene.List(graphene.String)
    
    class Arguments:
        input = CreateCommentInput(required=True)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return CreateComment(
                success=False,
                message="Authentication required",
                errors=["You must be logged in to comment"]
            )
        
        try:
                # Verify post exists
            post = Post.objects.get(id=input.post_id, is_deleted=False)
        except Post.DoesNotExist:
            return CreateComment(
                success=False,
                message="Post not found",
                errors=["Invalid post ID"]
            )
        
                # Verify parent comment if specified
        try:
            parent_comment = None
            if input.parent_comment_id:
                try:
                    parent_comment = Comment.objects.get(
                        id=input.parent_comment_id,
                        post=post,
                        is_deleted=False
                    )
                except Comment.DoesNotExist:
                    return CreateComment(
                        success=False,
                            message="Parent comment not found",
                            errors=["Invalid parent comment ID"]
                        )
                
            if not input.content.strip():
                return CreateComment(
                    success=False,
                    message="Comment cannot be empty",
                    errors=["Content is required"]
                )
                
            comment = Comment.objects.create(
                post=post,
                user=user,
                parent_comment=parent_comment,
                content=input.content.strip()
            )
            
            return CreateComment(
                success=True,
                message="Comment created successfully",
                comment=comment,
                errors=[]
               )
                
        except Exception as e:
            return CreateComment(
                success=False,
                message="An error occurred while creating the comment",
                errors=[str(e)]
            )

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

class SharePost(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    share = graphene.Field(ShareType)
    errors = graphene.List(graphene.String)
    
    class Arguments:
        input = SharePostInput(required=True)
    
    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return SharePost(
                success=False,
                message="Authentication required",
                errors=["You must be logged in to share"]
            )
        
        try:
            post = Post.objects.get(id=input.post_id, is_deleted=False)
        except Post.DoesNotExist:
            return SharePost(
                success=False,
                message="Post not found",
                errors=["Invalid post ID"]
            )
        
        try:
            # Check if already shared
            share, created = Share.objects.get_or_create(
                post=post,
                user=user,
                defaults={'caption': input.caption}
            )
            
            if created:
                return SharePost(
                    success=True,
                    message="Post shared successfully",
                    share=share,
                    errors=[]
                )
            else:
                return SharePost(
                    success=True,
                    message="Post already shared",
                    share=share,
                    errors=[]
                )
                
        except Exception as e:
            return SharePost(
                success=False,
                message="An error occurred while sharing the post",
                errors=[str(e)]
            )

class FollowUser(graphene.Mutation):
    success = graphene.Boolean()
    following = graphene.Boolean()
    message = graphene.String()
    follower = graphene.Field(CustomUserType)
    followee = graphene.Field(CustomUserType)
    
    class Arguments:
        user_id = graphene.ID(required=True)
    
    def mutate(self, info, user_id):
        user = info.context.user
        if not user.is_authenticated:
            return FollowUser(
                success=False,
                message="Authentication required"
            )
        
        if str(user.id) == str(user_id):
            return FollowUser(
                success=False,
                message="You cannot follow yourself"
            )
        
        try:
            followee = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return FollowUser(
                success=False,
                message="User not found"
            )
        
        try:
            follow, created = Follow.objects.get_or_create(
                follower=user,
                followee=followee
            )
            
            if created:
                return FollowUser(
                    success=True,
                    following=True,
                    message=f"Now following {followee.username}",
                    follower=user,
                    followee=followee
                )
            else:
                return FollowUser(
                    success=True,
                    following=True,
                    message=f"Already following {followee.username}",
                    follower=user,
                    followee=followee
                )
                
        except Exception as e:
            return FollowUser(
                success=False,
                message=f"An error occurred: {str(e)}"
            )

class UnfollowUser(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    followee = graphene.Field(CustomUserType)
    
    class Arguments:
        user_id = graphene.ID(required=True)
    
    def mutate(self, info, user_id):
        user = info.context.user
        if not user.is_authenticated:
            return UnfollowUser(
                success=False,
                message="Authentication required"
            )
        
        try:
            followee = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return UnfollowUser(
                success=False,
                message="User not found"
            )
        
        try:
            follow = Follow.objects.get(follower=user, followee=followee)
            follow.delete()
            
            return UnfollowUser(
                success=True,
                message=f"Unfollowed {followee.username}",
                followee=followee
            )
            
        except Follow.DoesNotExist:
            return UnfollowUser(
                success=True,
                message=f"You were not following {followee.username}",
                followee=followee
            )
            
class Mutation(graphene.ObjectType):
    """This is where you register all your mutations"""
    
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_comment = CreateComment.Field()
    like_post = LikePost.Field()
    unlike_post = UnlikePost.Field()
    share_post = SharePost.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)
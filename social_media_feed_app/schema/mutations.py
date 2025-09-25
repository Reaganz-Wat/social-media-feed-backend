import graphene
import graphql_jwt
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .types import *
from .inputs import *
from social_media_feed_app.models import *

class RegisterUser(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(CustomUserType)
    errors = graphene.List(graphene.String)
    
    class Arguments:
        input = RegisterUserInput(required=True)
    
    def mutate(self, info, input):
        errors = []
        
        # Validate email format
        try:
            validate_email(input.email)
        except ValidationError:
            errors.append("Invalid email format")
        
        # Check if username already exists
        if CustomUser.objects.filter(username=input.username).exists():
            errors.append("Username already exists")
        
        # Check if email already exists
        if CustomUser.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
        
        # Validate password strength
        if len(input.password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Validate username
        if len(input.username) < 3:
            errors.append("Username must be at least 3 characters long")
        
        if errors:
            return RegisterUser(
                success=False,
                message="Registration failed",
                errors=errors
            )
        
        try:
            user = CustomUser.objects.create_user(
                username=input.username,
                email=input.email,
                password=input.password,
                first_name=input.first_name,
                last_name=input.last_name,
                bio=input.bio
            )
            
            return RegisterUser(
                success=True,
                message=f"User {user.username} registered successfully",
                user=user,
                errors=[]
            )
            
        except Exception as e:
            return RegisterUser(
                success=False,
                message="An error occurred during registration",
                errors=[str(e)]
            )

class UpdateUserProfile(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(CustomUserType)
    errors = graphene.List(graphene.String)
    
    class Arguments:
        input = UpdateUserProfileInput(required=True)
    
    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateUserProfile(
                success=False,
                message="Authentication required",
                errors=["You must be logged in"]
            )
        
        errors = []
        
        try:
            # Check username uniqueness if being changed
            if input.username and input.username != user.username:
                if CustomUser.objects.filter(username=input.username).exists():
                    errors.append("Username already exists")
            
            if errors:
                return UpdateUserProfile(
                    success=False,
                    message="Update failed",
                    errors=errors
                )
            
            # Update fields
            if input.first_name is not None:
                user.first_name = input.first_name
            if input.last_name is not None:
                user.last_name = input.last_name
            if input.bio is not None:
                user.bio = input.bio
            if input.username is not None:
                user.username = input.username
            
            user.save()
            
            return UpdateUserProfile(
                success=True,
                message="Profile updated successfully",
                user=user,
                errors=[]
            )
            
        except Exception as e:
            return UpdateUserProfile(
                success=False,
                message="An error occurred while updating profile",
                errors=[str(e)]
            )

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
                message="Post created successfully",
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
    # Authentication
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    
    # User mutations
    register_user = RegisterUser.Field()
    update_user_profile = UpdateUserProfile.Field()
    
    # Post mutations
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_comment = CreateComment.Field()
    like_post = LikePost.Field()
    unlike_post = UnlikePost.Field()
    share_post = SharePost.Field()
    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()
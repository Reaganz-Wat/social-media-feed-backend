import graphene
from graphene_django import DjangoObjectType
from social_media_feed_app.models import (
    Comment, CommentLike, CustomUser, Post, PostLike, 
    Share, Follow, Friendship, Message, Interaction
)

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = "__all__"
        
class PostType(DjangoObjectType):
    likes_count = graphene.Int()
    comment_count = graphene.Int()
    share_count = graphene.Int()
    is_liked_by_user = graphene.Boolean()
    
    class Meta:
        model = Post
        fields = "__all__"
        
    def resolve_likes_count(self, info):
        return self.likes.count()
    
    def resolve_comment_count(self, info):
        return self.comments.filter(is_deleted=False).count()
    
    def resolve_share_count(self, info):
        return self.shares.count()
    
    def resolve_is_liked_by_user(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
        
class CommentType(DjangoObjectType):
    likes_count = graphene.Int()
    is_liked_by_user = graphene.Boolean()
    
    class Meta:
        model = Comment
        fields = "__all__"
    
    def resolve_likes_count(self, info):
        return self.likes.count()
    
    def resolve_is_liked_by_user(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
        
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
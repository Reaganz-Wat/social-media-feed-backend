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

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = "__all__"
        
class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = "__all__"
        
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
        
class Query(graphene.ObjectType):
    all_users = graphene.List(CustomUserType)
    all_posts = graphene.List(PostType)
    all_comments = graphene.List(CommentType)
    all_comment_likes = graphene.List(CommentLikeType)
    all_post_likes = graphene.List(PostLikeType)
    all_shares = graphene.List(ShareType)
    all_follows = graphene.List(FollowType)
    all_friends = graphene.List(FriendshipType)
    all_messages = graphene.List(MessageType)
    all_interactions = graphene.List(InteractionType)
    
    def resolve_all_users(root, info):
        return CustomUser.objects.all()
    
    def resolve_all_posts(root, info):
        return Post.objects.all()
    
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
    
schema = graphene.Schema(query=Query)
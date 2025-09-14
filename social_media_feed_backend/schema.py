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
        
class Query(graphene.ObjectType):
    all_users = graphene.List(CustomUserType)
    all_posts = graphene.List(PostType)
    
    def resolve_all_users(root, info):
        return CustomUser.objects.all()
    
    def resolve_all_posts(root, info):
        return Post.objects.all()
    
schema = graphene.Schema(query=Query)
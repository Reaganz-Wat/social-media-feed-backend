from django.contrib import admin
from .models import CustomUser, Post, PostLike, Comment, CommentLike, Follow, Friendship, Message, Interaction, Share

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(PostLike)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(Follow)
admin.site.register(Friendship)
admin.site.register(Message)
admin.site.register(Interaction)
admin.site.register(Share)
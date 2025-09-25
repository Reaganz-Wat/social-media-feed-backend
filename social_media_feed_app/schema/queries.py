import graphene
from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .types import *
from social_media_feed_app.models import *

class Query(graphene.ObjectType):
    # Post queries
    all_posts = graphene.List(
        PostType, 
        limit=graphene.Int(default_value=10), 
        offset=graphene.Int(default_value=0), 
        user_id=graphene.ID()
    )
    post_by_id = graphene.Field(PostType, id=graphene.ID(required=True))
    trending_posts = graphene.List(
        PostType, 
        limit=graphene.Int(default_value=12), 
        hours=graphene.Int(default_value=24)
    )
    user_feed = graphene.List(
        PostType,
        limit=graphene.Int(default_value=10),
        offset=graphene.Int(default_value=0)
    )
    
    # Comment queries
    post_comments = graphene.List(CommentType, post_id=graphene.ID(required=True))
    comment_replies = graphene.List(CommentType, comment_id=graphene.ID(required=True))
    
    # User queries
    user_by_id = graphene.Field(CustomUserType, id=graphene.ID(required=True))
    user_stats = graphene.Field(UserStatsType, id=graphene.ID(required=True))
    search_users = graphene.List(CustomUserType, query=graphene.String(required=True))
    
    def resolve_all_posts(self, info, limit=10, offset=0, user_id=None):
        queryset = Post.objects.filter(is_deleted=False).select_related('user').prefetch_related('likes', 'comments', 'shares')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        queryset = queryset.order_by('-created_at')
        return queryset[offset:offset + limit]
    
    def resolve_post_by_id(self, info, id):
        try:
            return Post.objects.select_related('user').prefetch_related(
                'comments__user',
                'likes__user',
                'shares__user'
            ).get(id=id, is_deleted=False)
        except Post.DoesNotExist:
            return None
        
    def resolve_user_feed(self, info, limit=10, offset=0):
        user = info.context.user
        if not user.is_authenticated:
            return []
        
        following_users = Follow.objects.filter(follower=user).values_list('followee_id', flat=True)
        user_ids = list(following_users) + [user.id]
        
        queryset = Post.objects.filter(
            user_id__in=user_ids,
            is_deleted=False
        ).select_related('user').prefetch_related('likes', 'comments', 'shares')
        
        queryset = queryset.order_by('-created_at')
        return queryset[offset:offset + limit]
    
    def resolve_post_comments(self, info, post_id):
        return Comment.objects.filter(
            post_id=post_id,
            parent_comment=None,
            is_deleted=False
        ).select_related('user').prefetch_related('replies', 'likes').order_by('created_at')
    
    def resolve_comment_replies(self, info, comment_id):
        return Comment.objects.filter(
            parent_comment_id=comment_id,
            is_deleted=False
        ).select_related('user').prefetch_related('likes').order_by('created_at')
    
    def resolve_trending_posts(self, info, limit=10, hours=24):
        time_threshold = timezone.now() - timedelta(hours=hours)
        
        queryset = Post.objects.filter(
            created_at__gte=time_threshold,
            is_deleted=False
        ).annotate(
            recent_likes=Count('likes', filter=Q(likes__created_at__gte=time_threshold)),
            recent_comments=Count('comments', filter=Q(comments__created_at__gte=time_threshold, comments__is_deleted=False)),
            recent_shares=Count('shares', filter=Q(shares__created_at__gte=time_threshold)),
            engagement_score=F('recent_likes') + F('recent_comments') * 2 + F('recent_shares') * 3
        ).select_related('user').prefetch_related('likes', 'comments', 'shares')
        
        return queryset.order_by('-engagement_score')[:limit]
    
    def resolve_user_by_id(self, info, id):
        try:
            return CustomUser.objects.prefetch_related(
                'posts', 'followers', 'following'
            ).get(id=id)
        except CustomUser.DoesNotExist:
            return None
        
    def resolve_user_stats(self, info, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return None
        
        total_posts = user.posts.filter(is_deleted=False).count()
        total_likes = PostLike.objects.filter(post__user=user).count()
        total_comments = Comment.objects.filter(post__user=user, is_deleted=False).count()
        total_shares = Share.objects.filter(post__user=user).count()
        followers_count = user.followers.count()
        following_count = user.following.count()
        
        total_engagement = total_likes + total_comments + total_shares
        engagement_rate = (total_engagement / max(total_posts, 1)) if total_posts > 0 else 0
        
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
    
    def resolve_search_users(self, info, query):
        return CustomUser.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )[:10]
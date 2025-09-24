from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .models import CustomUser, Post, PostLike, Comment, Follow, Interaction

@receiver(post_save, sender=CustomUser)
def user_created_handler(sender, instance, created, **kwargs):
    """Handle actions when a new user is created"""
    if created:
        print(f"New user registered: {instance.username} ({instance.email})")
        
        # Create welcome interaction
        Interaction.objects.create(
            user=instance,
            target_type='user',
            target_id=instance.id,
            interaction_type='view',
            metadata={'action': 'user_registered', 'timestamp': instance.created_at.isoformat()}
        )
        
        # You could also:
        # - Send welcome email
        # - Create default user settings
        # - Add to default groups
        # - Create notification preferences

@receiver(post_save, sender=Post)
def post_created_handler(sender, instance, created, **kwargs):
    """Handle actions when a new post is created"""
    if created:
        print(f"New post created by {instance.user.username}: {instance.title or instance.content[:50]}...")
        
        # Create interaction record
        Interaction.objects.create(
            user=instance.user,
            target_type='post',
            target_id=instance.id,
            interaction_type='view',
            metadata={'action': 'post_created'}
        )

@receiver(post_save, sender=PostLike)
def post_liked_handler(sender, instance, created, **kwargs):
    """Handle when a post is liked"""
    if created:
        # Create interaction record
        Interaction.objects.create(
            user=instance.user,
            target_type='post',
            target_id=instance.post.id,
            interaction_type='like',
            metadata={'liked_user_id': str(instance.post.user.id)}
        )
        
        print(f"{instance.user.username} liked {instance.post.user.username}'s post")

@receiver(post_save, sender=Comment)
def comment_created_handler(sender, instance, created, **kwargs):
    """Handle when a comment is created"""
    if created:
        # Create interaction record
        Interaction.objects.create(
            user=instance.user,
            target_type='comment',
            target_id=instance.id,
            interaction_type='comment',
            metadata={
                'post_id': str(instance.post.id),
                'post_owner_id': str(instance.post.user.id)
            }
        )

@receiver(post_save, sender=Follow)
def user_followed_handler(sender, instance, created, **kwargs):
    """Handle when someone follows a user"""
    if created:
        # Create interaction record
        Interaction.objects.create(
            user=instance.follower,
            target_type='user',
            target_id=instance.followee.id,
            interaction_type='follow',
            metadata={'followed_user_id': str(instance.followee.id)}
        )
        
        print(f"{instance.follower.username} started following {instance.followee.username}")

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """Handle when user logs in"""
    print(f"User {user.username} logged in from IP: {request.META.get('REMOTE_ADDR')}")
    
    # Create login interaction
    Interaction.objects.create(
        user=user,
        target_type='user',
        target_id=user.id,
        interaction_type='view',
        metadata={
            'action': 'user_login',
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
    )
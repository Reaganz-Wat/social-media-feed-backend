from django.db import migrations

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('social_media_feed_app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="-- Cannot drop extension safely"
        ),
        
        migrations.RunSQL(
            sql="""
            -- User authentication indexes
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_user_email ON social_media_feed_app_customuser(email);
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_user_username ON social_media_feed_app_customuser(username);
            
            -- Feed generation indexes (CRITICAL)
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_feed ON social_media_feed_app_post(user_id, created_at DESC, is_deleted) WHERE is_deleted = false;
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_timeline ON social_media_feed_app_post(created_at DESC, is_deleted) WHERE is_deleted = false;
            
            -- Follow system indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_follow_follower ON social_media_feed_app_follow(follower_id, created_at DESC);
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_follow_unique ON social_media_feed_app_follow(follower_id, followee_id);
            
            -- Like system indexes
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_postlike_unique ON social_media_feed_app_postlike(post_id, user_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_postlike_count ON social_media_feed_app_postlike(post_id, created_at);
            
            -- Comment system indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_thread ON social_media_feed_app_comment(post_id, parent_comment_id, created_at) WHERE is_deleted = false;
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_comment_toplevel ON social_media_feed_app_comment(post_id, created_at) WHERE parent_comment_id IS NULL AND is_deleted = false;
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_commentlike_unique ON social_media_feed_app_commentlike(comment_id, user_id);
            
            -- Share system indexes
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_share_unique ON social_media_feed_app_share(post_id, user_id);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_share_count ON social_media_feed_app_share(post_id, created_at);
            
            -- Search indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_search_username ON social_media_feed_app_customuser USING gin(username gin_trgm_ops);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_search_name ON social_media_feed_app_customuser USING gin((first_name || ' ' || last_name) gin_trgm_ops);
            
            -- Trending posts indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_trending ON social_media_feed_app_post(created_at, is_deleted) WHERE is_deleted = false AND created_at >= (NOW() - INTERVAL '7 days');
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_postlike_trending ON social_media_feed_app_postlike(created_at, post_id) WHERE created_at >= (NOW() - INTERVAL '7 days');
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_share_trending ON social_media_feed_app_share(created_at, post_id) WHERE created_at >= (NOW() - INTERVAL '7 days');
            
            -- Messaging indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_conversation ON social_media_feed_app_message(sender_id, receiver_id, created_at DESC);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_message_unread ON social_media_feed_app_message(receiver_id, is_read, created_at DESC) WHERE is_read = false;
            
            -- Friendship indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_friendship_requester ON social_media_feed_app_friendship(requester_id, status, updated_at DESC);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_friendship_receiver ON social_media_feed_app_friendship(receiver_id, status, updated_at DESC);
            
            -- Analytics indexes
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_interaction_user_type ON social_media_feed_app_interaction(user_id, interaction_type, created_at DESC);
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_interaction_target ON social_media_feed_app_interaction(target_type, target_id, interaction_type);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS idx_user_email;
            DROP INDEX IF EXISTS idx_user_username;
            DROP INDEX IF EXISTS idx_post_feed;
            DROP INDEX IF EXISTS idx_post_timeline;
            DROP INDEX IF EXISTS idx_follow_follower;
            DROP INDEX IF EXISTS idx_follow_unique;
            DROP INDEX IF EXISTS idx_postlike_unique;
            DROP INDEX IF EXISTS idx_postlike_count;
            DROP INDEX IF EXISTS idx_comment_thread;
            DROP INDEX IF EXISTS idx_comment_toplevel;
            DROP INDEX IF EXISTS idx_commentlike_unique;
            DROP INDEX IF EXISTS idx_share_unique;
            DROP INDEX IF EXISTS idx_share_count;
            DROP INDEX IF EXISTS idx_user_search_username;
            DROP INDEX IF EXISTS idx_user_search_name;
            DROP INDEX IF EXISTS idx_post_trending;
            DROP INDEX IF EXISTS idx_postlike_trending;
            DROP INDEX IF EXISTS idx_share_trending;
            DROP INDEX IF EXISTS idx_message_conversation;
            DROP INDEX IF EXISTS idx_message_unread;
            DROP INDEX IF EXISTS idx_friendship_requester;
            DROP INDEX IF EXISTS idx_friendship_receiver;
            DROP INDEX IF EXISTS idx_interaction_user_type;
            DROP INDEX IF EXISTS idx_interaction_target;
            """
        ),
    ]
import uuid
import logging
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import Mock
from social_media_feed_app.models import (
    Post, Comment, PostLike, CommentLike, Share, Follow, CustomUser
)
from .schema.queries import Query
from .schema.mutations import (
    RegisterUser, CreatePost, UpdatePost, DeletePost, LikePost, 
    UnlikePost, CreateComment, SharePost, FollowUser, UnfollowUser,
    UpdateUserProfile
)

# Disable logging during tests
logging.disable(logging.CRITICAL)

User = get_user_model()


class GraphQLTestCase(TestCase):
    """Tests for GraphQL queries and mutations"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = CustomUser.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User1',
            bio='Test bio for user 1'
        )
        
        self.user2 = CustomUser.objects.create_user(
            username='testuser2', 
            email='test2@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User2',
            bio='Test bio for user 2'
        )
        
        # Create test posts
        self.post1 = Post.objects.create(
            user=self.user1,
            title="Test Post 1",
            content="This is test content for post 1",
            media_type="text"
        )
        
        self.post2 = Post.objects.create(
            user=self.user2,
            title="Test Post 2", 
            content="This is test content for post 2",
            media_type="image"
        )
        
        # Create test comment
        self.comment1 = Comment.objects.create(
            post=self.post1,
            user=self.user2,
            content="This is a test comment"
        )
        
        # Create query resolver instance
        self.query_resolver = Query()
        
        # Generate valid non-existent UUIDs for testing
        self.non_existent_uuid = str(uuid.uuid4())
        self.non_existent_user_uuid = str(uuid.uuid4())
    
    def create_mock_info(self, user=None):
        """Create mock GraphQL info object"""
        mock_context = Mock()
        mock_context.user = user if user else self.user1
        
        mock_info = Mock()
        mock_info.context = mock_context
        
        return mock_info
    
    def create_mock_input(self, **kwargs):
        """Create mock input object"""
        mock_input = Mock()
        for key, value in kwargs.items():
            setattr(mock_input, key, value)
        return mock_input


# ===== QUERY TESTS =====
class QueryTests(GraphQLTestCase):
    """Test GraphQL queries"""
    
    def test_all_posts_query(self):
        """Test fetching all posts"""
        info = self.create_mock_info()
        
        # Test basic query
        posts = self.query_resolver.resolve_all_posts(info, limit=10, offset=0)
        
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].title, "Test Post 2")  # Most recent first
        self.assertEqual(posts[1].title, "Test Post 1")
    
    def test_all_posts_with_user_filter(self):
        """Test fetching posts by specific user"""
        info = self.create_mock_info()
        
        posts = self.query_resolver.resolve_all_posts(info, limit=10, offset=0, user_id=str(self.user1.id))
        
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].user, self.user1)
    
    def test_all_posts_pagination(self):
        """Test posts pagination"""
        info = self.create_mock_info()
        
        # Test limit
        posts = self.query_resolver.resolve_all_posts(info, limit=1, offset=0)
        self.assertEqual(len(posts), 1)
        
        # Test offset
        posts = self.query_resolver.resolve_all_posts(info, limit=10, offset=1)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, "Test Post 1")
    
    def test_post_by_id_query(self):
        """Test fetching specific post by ID"""
        info = self.create_mock_info()
        
        # Test valid post
        post = self.query_resolver.resolve_post_by_id(info, id=str(self.post1.id))
        self.assertIsNotNone(post)
        self.assertEqual(post.title, "Test Post 1")
        
        # Test non-existent post (using valid UUID format)
        post = self.query_resolver.resolve_post_by_id(info, id=self.non_existent_uuid)
        self.assertIsNone(post)
    
    def test_user_feed_authenticated(self):
        """Test user feed for authenticated user"""
        # Create follow relationship
        Follow.objects.create(follower=self.user1, followee=self.user2)
        
        info = self.create_mock_info(self.user1)
        
        posts = self.query_resolver.resolve_user_feed(info, limit=10, offset=0)
        
        # Should include posts from user1 and user2 (followed)
        self.assertEqual(len(posts), 2)
    
    def test_user_feed_unauthenticated(self):
        """Test user feed for unauthenticated user"""
        mock_user = Mock()
        mock_user.is_authenticated = False
        
        info = self.create_mock_info(mock_user)
        
        posts = self.query_resolver.resolve_user_feed(info, limit=10, offset=0)
        
        self.assertEqual(posts, [])
    
    def test_trending_posts(self):
        """Test trending posts query"""
        # Add engagement to make post1 trending
        PostLike.objects.create(post=self.post1, user=self.user2)
        Comment.objects.create(post=self.post1, user=self.user2, content="Great!")
        Share.objects.create(post=self.post1, user=self.user2, caption="Awesome")
        
        info = self.create_mock_info()
        
        posts = self.query_resolver.resolve_trending_posts(info, limit=5, hours=24)
        
        self.assertGreaterEqual(len(posts), 1)
        # post1 should be first due to higher engagement
        self.assertEqual(posts[0], self.post1)
    
    def test_post_comments_query(self):
        """Test fetching comments for a post"""
        info = self.create_mock_info()
        
        comments = self.query_resolver.resolve_post_comments(info, post_id=str(self.post1.id))
        
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].content, "This is a test comment")
        self.assertEqual(comments[0].user, self.user2)
    
    def test_comment_replies_query(self):
        """Test fetching replies to a comment"""
        # Create a reply
        reply = Comment.objects.create(
            post=self.post1,
            user=self.user1,
            parent_comment=self.comment1,
            content="This is a reply"
        )
        
        info = self.create_mock_info()
        
        replies = self.query_resolver.resolve_comment_replies(info, comment_id=str(self.comment1.id))
        
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].content, "This is a reply")
        self.assertEqual(replies[0].parent_comment, self.comment1)
    
    def test_user_by_id_query(self):
        """Test fetching user by ID"""
        info = self.create_mock_info()
        
        # Test valid user
        user = self.query_resolver.resolve_user_by_id(info, id=str(self.user1.id))
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser1')
        
        # Test non-existent user (using valid UUID format)
        user = self.query_resolver.resolve_user_by_id(info, id=self.non_existent_user_uuid)
        self.assertIsNone(user)
    
    def test_search_users_query(self):
        """Test searching users"""
        info = self.create_mock_info()
        
        # Search by username
        users = self.query_resolver.resolve_search_users(info, query='testuser1')
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'testuser1')
        
        # Search by first name
        users = self.query_resolver.resolve_search_users(info, query='Test')
        self.assertEqual(len(users), 2)
    
    def test_user_stats_query(self):
        """Test user statistics calculation"""
        # Add some engagement data
        PostLike.objects.create(post=self.post1, user=self.user2)
        Comment.objects.create(post=self.post1, user=self.user2, content="Great!")
        Share.objects.create(post=self.post1, user=self.user2, caption="Awesome")
        Follow.objects.create(follower=self.user2, followee=self.user1)
        
        info = self.create_mock_info()
        
        stats = self.query_resolver.resolve_user_stats(info, id=str(self.user1.id))
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.total_posts, 1)
        self.assertEqual(stats.total_likes, 1)
        self.assertEqual(stats.followers_count, 1)
        self.assertIsNotNone(stats.top_performing_post)


# ===== MUTATION TESTS =====
class MutationTests(GraphQLTestCase):
    """Test GraphQL mutations"""
    
    def test_register_user_success(self):
        """Test successful user registration"""
        mutation = RegisterUser()
        
        input_data = self.create_mock_input(
            username='newuser',
            email='newuser@example.com',
            password='newpass123',
            first_name='New',
            last_name='User',
            bio='Test bio'
        )
        
        info = self.create_mock_info()
        result = mutation.mutate(info, input=input_data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.user.username, 'newuser')
        self.assertEqual(len(result.errors), 0)
        
        # Verify user was created in database
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())
    
    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username"""
        mutation = RegisterUser()
        
        input_data = self.create_mock_input(
            username='testuser1',  # Already exists
            email='new@example.com',
            password='newpass123',
            first_name='New',
            last_name='User',
            bio='Test bio'
        )
        
        info = self.create_mock_info()
        result = mutation.mutate(info, input=input_data)
        
        self.assertFalse(result.success)
        self.assertIn("Username already exists", result.errors)
    
    def test_register_user_invalid_email(self):
        """Test registration with invalid email"""
        mutation = RegisterUser()
        
        input_data = self.create_mock_input(
            username='newuser',
            email='invalid-email',
            password='newpass123',
            first_name='New',
            last_name='User',
            bio='Test bio'
        )
        
        info = self.create_mock_info()
        result = mutation.mutate(info, input=input_data)
        
        self.assertFalse(result.success)
        self.assertIn("Invalid email format", result.errors)
    
    def test_register_user_short_password(self):
        """Test registration with short password"""
        mutation = RegisterUser()
        
        input_data = self.create_mock_input(
            username='newuser',
            email='new@example.com',
            password='short',
            first_name='New',
            last_name='User',
            bio='Test bio'
        )
        
        info = self.create_mock_info()
        result = mutation.mutate(info, input=input_data)
        
        self.assertFalse(result.success)
        self.assertIn("Password must be at least 8 characters long", result.errors)
    
    def test_create_post_success(self):
        """Test successful post creation"""
        mutation = CreatePost()
        
        # Using the correct signature from mutations.py
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(
            info, 
            user_id=str(self.user1.id),
            content='This is new post content',
            title='New Test Post',
            media_type='text'
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.post.title, 'New Test Post')
        self.assertEqual(result.post.user, self.user1)
        
        # Verify post was created in database
        self.assertTrue(Post.objects.filter(title='New Test Post').exists())
    
    def test_create_post_invalid_user(self):
        """Test creating post with invalid user ID"""
        mutation = CreatePost()
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(
            info,
            user_id=self.non_existent_user_uuid,  # Use valid UUID format
            content='This is new post content',
            title='New Test Post',
            media_type='text'
        )
        
        self.assertFalse(result.success)
        self.assertIn("User not found", result.message)
    
    def test_create_post_empty_content(self):
        """Test creating post with empty content"""
        mutation = CreatePost()
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(
            info,
            user_id=str(self.user1.id),
            content='   ',  # Empty/whitespace only
            title='New Test Post',
            media_type='text'
        )
        
        self.assertFalse(result.success)
        self.assertIn("Content cannot be empty", result.message)
    
    def test_update_post_success(self):
        """Test successful post update"""
        mutation = UpdatePost()
        
        input_data = self.create_mock_input(
            title='Updated Title',
            content='Updated content',
            media_type='image'
        )
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, id=str(self.post1.id), input=input_data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.post.title, 'Updated Title')
        
        # Verify post was updated in database
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, 'Updated Title')
    
    def test_update_post_unauthorized(self):
        """Test updating post by different user"""
        mutation = UpdatePost()
        
        input_data = self.create_mock_input(
            title='Updated Title',
            content='Updated content'
        )
        
        info = self.create_mock_info(self.user2)  # Different user
        result = mutation.mutate(info, id=str(self.post1.id), input=input_data)
        
        self.assertFalse(result.success)
        self.assertIn("permission", result.message.lower())
    
    def test_delete_post_success(self):
        """Test successful post deletion"""
        mutation = DeletePost()
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, id=str(self.post1.id))
        
        self.assertTrue(result.success)
        
        # Verify post is soft deleted
        self.post1.refresh_from_db()
        self.assertTrue(self.post1.is_deleted)
    
    def test_like_post_success(self):
        """Test liking a post"""
        mutation = LikePost()
        
        info = self.create_mock_info(self.user2)
        result = mutation.mutate(info, post_id=str(self.post1.id))
        
        self.assertTrue(result.success)
        self.assertTrue(result.liked)
        
        # Verify like was created
        self.assertTrue(PostLike.objects.filter(post=self.post1, user=self.user2).exists())
    
    def test_like_post_already_liked(self):
        """Test liking an already liked post"""
        # Create existing like
        PostLike.objects.create(post=self.post1, user=self.user2)
        
        mutation = LikePost()
        
        info = self.create_mock_info(self.user2)
        result = mutation.mutate(info, post_id=str(self.post1.id))
        
        self.assertTrue(result.success)
        self.assertTrue(result.liked)
        self.assertIn("already liked", result.message.lower())
    
    def test_unlike_post_success(self):
        """Test unliking a post"""
        # Create existing like
        PostLike.objects.create(post=self.post1, user=self.user2)
        
        mutation = UnlikePost()
        
        info = self.create_mock_info(self.user2)
        result = mutation.mutate(info, post_id=str(self.post1.id))
        
        self.assertTrue(result.success)
        
        # Verify like was removed
        self.assertFalse(PostLike.objects.filter(post=self.post1, user=self.user2).exists())
    
    def test_create_comment_success(self):
        """Test creating a comment"""
        mutation = CreateComment()
        
        input_data = self.create_mock_input(
            post_id=str(self.post1.id),
            content='This is a new comment',
            parent_comment_id=None
        )
        
        info = self.create_mock_info(self.user2)
        result = mutation.mutate(info, input=input_data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.comment.content, 'This is a new comment')
        self.assertEqual(result.comment.post, self.post1)
        
        # Verify comment was created
        self.assertTrue(Comment.objects.filter(content='This is a new comment').exists())
    
    def test_create_comment_reply(self):
        """Test creating a reply to a comment"""
        mutation = CreateComment()
        
        input_data = self.create_mock_input(
            post_id=str(self.post1.id),
            content='This is a reply',
            parent_comment_id=str(self.comment1.id)
        )
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, input=input_data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.comment.parent_comment, self.comment1)
    
    def test_share_post_success(self):
        """Test sharing a post"""
        mutation = SharePost()
        
        input_data = self.create_mock_input(
            post_id=str(self.post1.id),
            caption='Check this out!'
        )
        
        info = self.create_mock_info(self.user2)
        result = mutation.mutate(info, input=input_data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.share.caption, 'Check this out!')
        
        # Verify share was created
        self.assertTrue(Share.objects.filter(post=self.post1, user=self.user2).exists())
    
    def test_follow_user_success(self):
        """Test following a user"""
        mutation = FollowUser()
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, user_id=str(self.user2.id))
        
        self.assertTrue(result.success)
        self.assertTrue(result.following)
        
        # Verify follow relationship was created
        self.assertTrue(Follow.objects.filter(follower=self.user1, followee=self.user2).exists())
    
    def test_follow_self_error(self):
        """Test following oneself (should fail)"""
        mutation = FollowUser()
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, user_id=str(self.user1.id))
        
        self.assertFalse(result.success)
        self.assertIn("cannot follow yourself", result.message.lower())
    
    def test_unfollow_user_success(self):
        """Test unfollowing a user"""
        # Create existing follow relationship
        Follow.objects.create(follower=self.user1, followee=self.user2)
        
        mutation = UnfollowUser()
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, user_id=str(self.user2.id))
        
        self.assertTrue(result.success)
        
        # Verify follow relationship was removed
        self.assertFalse(Follow.objects.filter(follower=self.user1, followee=self.user2).exists())
    
    def test_update_user_profile_success(self):
        """Test updating user profile"""
        mutation = UpdateUserProfile()
        
        input_data = self.create_mock_input(
            first_name='Updated',
            last_name='Name',
            bio='Updated bio',
            username='updateduser'
        )
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, input=input_data)
        
        self.assertTrue(result.success)
        self.assertEqual(result.user.first_name, 'Updated')
        self.assertEqual(result.user.username, 'updateduser')
        
        # Verify user was updated in database
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')


# ===== EDGE CASE TESTS =====
class EdgeCaseTests(GraphQLTestCase):
    """Test edge cases and error conditions"""
    
    def test_query_deleted_post(self):
        """Test querying a deleted post"""
        self.post1.is_deleted = True
        self.post1.save()
        
        info = self.create_mock_info()
        post = self.query_resolver.resolve_post_by_id(info, id=str(self.post1.id))
        
        self.assertIsNone(post)
    
    def test_comment_on_deleted_post(self):
        """Test commenting on a deleted post"""
        self.post1.is_deleted = True
        self.post1.save()
        
        mutation = CreateComment()
        
        input_data = self.create_mock_input(
            post_id=str(self.post1.id),
            content='Comment on deleted post',
            parent_comment_id=None
        )
        
        info = self.create_mock_info(self.user2)
        result = mutation.mutate(info, input=input_data)
        
        self.assertFalse(result.success)
        self.assertIn("Post not found", result.message)
    
    def test_like_nonexistent_post(self):
        """Test liking a non-existent post"""
        mutation = LikePost()
        
        info = self.create_mock_info(self.user2)
        result = mutation.mutate(info, post_id=self.non_existent_uuid)
        
        self.assertFalse(result.success)
        self.assertIn("Post not found", result.message)
    
    def test_follow_nonexistent_user(self):
        """Test following a non-existent user"""
        mutation = FollowUser()
        
        info = self.create_mock_info(self.user1)
        result = mutation.mutate(info, user_id=self.non_existent_user_uuid)
        
        self.assertFalse(result.success)
        self.assertIn("User not found", result.message)
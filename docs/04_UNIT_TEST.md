# Social Media Feed API Testing Documentation

This document provides comprehensive guidance for testing the GraphQL API in the social media feed backend project. The test suite ensures the reliability and correctness of all GraphQL queries and mutations.

## Table of Contents

- [Overview](#overview)
- [Database Configuration](#database-configuration)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Understanding Test Output](#understanding-test-output)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The testing strategy uses Django's built-in testing framework to ensure comprehensive coverage of:

- ✅ **All GraphQL Queries** - User feeds, posts, comments, search functionality
- ✅ **All GraphQL Mutations** - User registration, CRUD operations, social interactions
- ✅ **Authentication & Authorization** - Permission checks and user context
- ✅ **Error Handling** - Invalid inputs, missing resources, edge cases
- ✅ **Business Logic** - Engagement scoring, user statistics, content filtering

## Database Configuration

### Test Database Setup

The test suite uses **SQLite in-memory database** for testing while preserving your production database:

```python
# In settings.py
import sys
if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Fast in-memory database
    }
```

### Why SQLite for Testing?

| Benefit | Description |
|---------|-------------|
| **Speed** | In-memory SQLite is much faster than disk-based databases |
| **Isolation** | Each test run gets a fresh database |
| **Safety** | No risk of affecting production/development data |
| **Simplicity** | No additional database setup required |

### Database Locations

- **Production**: Your configured database (PostgreSQL, MySQL, etc.)
- **Development**: Your configured database
- **Testing**: SQLite in-memory (`:memory:`) - no files created

## Test Structure

### File Organization

```
social_media_feed_app/
├── models.py
├── schema/
│   ├── queries.py
│   ├── mutations.py
│   ├── types.py
│   └── inputs.py
├── tests.py          # ← Main test file
└── ...
```

### Test Classes

#### 1. `QueryTests` - GraphQL Query Testing

Tests all query resolvers with various scenarios:

```python
class QueryTests(GraphQLTestCase):
    def test_all_posts_query(self):
        """Test fetching all posts with pagination"""
        
    def test_user_feed_authenticated(self):
        """Test personalized user feed"""
        
    def test_trending_posts(self):
        """Test engagement-based trending algorithm"""
```

**Covered Queries:**
- `allPosts` - Post listing with filters and pagination
- `postById` - Individual post retrieval
- `userFeed` - Personalized content feed based on follows
- `trendingPosts` - Algorithm-based trending content with engagement scoring
- `postComments` - Comment threading and retrieval
- `commentReplies` - Nested comment system
- `userById` - User profile data
- `searchUsers` - User search by username and name
- `userStats` - Analytics and engagement metrics

#### 2. `MutationTests` - GraphQL Mutation Testing

Tests all mutation operations with success and error scenarios:

```python
class MutationTests(GraphQLTestCase):
    def test_register_user_success(self):
        """Test successful user registration"""
        
    def test_create_post_invalid_user(self):
        """Test authentication requirements"""
        
    def test_like_post_already_liked(self):
        """Test idempotent operations"""
```

**Covered Mutations:**
- `registerUser` - User account creation with validation
- `updateUserProfile` - Profile modification
- `createPost` - Content creation (using individual parameters, not input object)
- `updatePost` - Content modification with ownership checks
- `deletePost` - Soft deletion
- `likePost`/`unlikePost` - Engagement actions
- `createComment` - Comment creation and threading
- `sharePost` - Content sharing with captions
- `followUser`/`unfollowUser` - Social relationships

#### 3. `EdgeCaseTests` - Error Conditions & Edge Cases

Tests boundary conditions and error scenarios:

```python
class EdgeCaseTests(GraphQLTestCase):
    def test_query_deleted_post(self):
        """Test handling of soft-deleted content"""
        
    def test_follow_nonexistent_user(self):
        """Test error handling for invalid UUID references"""
```

## Running Tests

### Basic Commands

```bash
# Run all tests in the social media feed app
python manage.py test social_media_feed_app

# Run only GraphQL tests
python manage.py test social_media_feed_app.tests

# Run with verbose output
python manage.py test social_media_feed_app.tests --verbosity=2

# Run specific test class
python manage.py test social_media_feed_app.tests.QueryTests

# Run specific test method
python manage.py test social_media_feed_app.tests.QueryTests.test_all_posts_query
```

### Advanced Options

```bash
# Run tests in parallel (faster)
python manage.py test --parallel

# Keep test database between runs (faster for repeated testing)
python manage.py test --keepdb

# Combine options for fastest execution
python manage.py test social_media_feed_app --parallel --keepdb --verbosity=2
```

### Coverage Analysis

Install coverage tool:
```bash
pip install coverage
```

Run tests with coverage:
```bash
# Run tests with coverage
coverage run --source='.' manage.py test social_media_feed_app.tests

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

## Test Coverage

### Query Coverage (100%)

| Query | Test Methods | Scenarios Tested |
|-------|-------------|------------------|
| `allPosts` | 3 test methods | Basic query, user filtering, pagination |
| `postById` | 1 test method | Valid post, non-existent post (UUID format) |
| `userFeed` | 2 test methods | Authenticated user with follows, unauthenticated user |
| `trendingPosts` | 1 test method | Engagement scoring algorithm with likes, comments, shares |
| `postComments` | 1 test method | Comment retrieval and ordering |
| `commentReplies` | 1 test method | Nested comment threading |
| `userById` | 1 test method | Valid user, non-existent user (UUID format) |
| `searchUsers` | 1 test method | Username and name search |
| `userStats` | 1 test method | Analytics calculation with engagement data |

### Mutation Coverage (100%)

| Mutation | Test Methods | Scenarios Tested |
|----------|-------------|------------------|
| `registerUser` | 4 test methods | Success, duplicate username, invalid email, weak password |
| `updateUserProfile` | 1 test method | Profile field updates |
| `createPost` | 3 test methods | Success (with individual params), invalid user, empty content |
| `updatePost` | 2 test methods | Success, unauthorized access |
| `deletePost` | 1 test method | Soft deletion |
| `likePost` | 2 test methods | First like, already liked idempotency |
| `unlikePost` | 1 test method | Remove like |
| `createComment` | 2 test methods | Top-level comment, reply to comment |
| `sharePost` | 1 test method | Content sharing with caption |
| `followUser` | 2 test methods | Success, self-follow prevention |
| `unfollowUser` | 1 test method | Relationship removal |

### Authentication & Authorization

- ✅ **Unauthenticated requests** - Proper rejection of protected operations
- ✅ **User context** - Correct user association in mutations
- ✅ **Ownership checks** - Users can only modify their own content
- ✅ **Permission validation** - Appropriate access control

### Error Handling

- ✅ **Input validation** - Email format, password strength, content length
- ✅ **UUID validation** - Proper handling of malformed UUIDs
- ✅ **Resource existence** - Handling of non-existent posts, users, comments
- ✅ **Business rules** - Prevention of self-following, duplicate actions
- ✅ **Soft deletion** - Proper handling of deleted content

## Understanding Test Output

### Successful Test Run

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
....................................
----------------------------------------------------------------------
Ran 36 tests in 15.234s

OK
Destroying test database for alias 'default'...
```

### Test with Failures

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.....F........
======================================================================
FAIL: test_create_post_success (social_media_feed_app.tests.MutationTests)
Test successful post creation
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/path/to/tests.py", line 234, in test_create_post_success
    self.assertTrue(result.success)
AssertionError: False is not true
----------------------------------------------------------------------
Ran 36 tests in 15.123s

FAILED (failures=1)
```

### Verbose Output (--verbosity=2)

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
test_all_posts_query (social_media_feed_app.tests.QueryTests)
Test fetching all posts ... ok
test_all_posts_pagination (social_media_feed_app.tests.QueryTests)
Test posts pagination ... ok
test_create_post_success (social_media_feed_app.tests.MutationTests)
Test successful post creation ... ok
```

### Coverage Report

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
social_media_feed_app/models.py           85      2    98%
social_media_feed_app/schema/queries.py   78      0   100%
social_media_feed_app/schema/mutations.py 156     3    98%
social_media_feed_app/schema/types.py     23      0   100%
-----------------------------------------------------------
TOTAL                                     342      5    99%
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:**
```
ImportError: cannot import name 'Query' from 'social_media_feed_app.schema.queries'
```

**Solution:**
```python
# Check import paths in tests.py
from .schema.queries import Query
from .schema.mutations import RegisterUser, CreatePost, ...
```

#### 2. UUID Validation Errors

**Problem:**
```
django.core.exceptions.ValidationError: '"non-existent-id" is not a valid UUID.'
```

**Solution:**
```python
# Use proper UUID format in tests
self.non_existent_uuid = str(uuid.uuid4())
```

#### 3. CreatePost Mutation Signature

**Problem:**
```
TypeError: CreatePost.mutate() got an unexpected keyword argument 'input'
```

**Solution:**
```python
# Use individual parameters, not input object
result = mutation.mutate(
    info, 
    user_id=str(self.user1.id),
    content='Post content',
    title='Post Title',
    media_type='text'
)
```

#### 4. Excessive Logging During Tests

**Problem:** Too much output from model signals/methods

**Solution:**
```python
import logging
logging.disable(logging.CRITICAL)  # Add to tests.py
```

### Performance Issues

#### Slow Test Execution

1. **Use in-memory SQLite:**
   ```python
   DATABASES['default']['NAME'] = ':memory:'
   ```

2. **Disable migrations:**
   ```python
   MIGRATION_MODULES = DisableMigrations()
   ```

3. **Use faster password hashing:**
   ```python
   PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
   ```

4. **Run tests in parallel:**
   ```bash
   python manage.py test --parallel
   ```

## Best Practices

### Writing Tests

1. **Descriptive Test Names**
   ```python
   def test_create_post_with_empty_content_should_fail(self):
       # Clear what the test does and expects
   ```

2. **Test One Thing**
   ```python
   # Good: Tests one specific scenario
   def test_like_post_when_already_liked(self):
   
   # Avoid: Testing multiple scenarios in one test
   def test_post_interactions(self):
   ```

3. **Use Meaningful Assertions**
   ```python
   # Good: Clear what's being tested
   self.assertEqual(result.post.title, 'Expected Title')
   
   # Less clear: What exactly succeeded?
   self.assertTrue(result.success)
   ```

4. **Clean Test Data**
   ```python
   def setUp(self):
       # Create minimal data needed for tests
       self.user = CustomUser.objects.create_user(...)
   ```

### Test Organization

1. **Group Related Tests**
   ```python
   class QueryTests(GraphQLTestCase):
       # All query-related tests
   
   class MutationTests(GraphQLTestCase):
       # All mutation-related tests
   ```

2. **Use Clear Section Comments**
   ```python
   # ===== SUCCESS SCENARIOS =====
   def test_create_post_success(self):
   
   # ===== ERROR SCENARIOS =====
   def test_create_post_invalid_user(self):
   ```

### Project-Specific Notes

1. **UUID Fields**: All model IDs are UUIDs, so always use `str(uuid.uuid4())` for non-existent references
2. **CreatePost Signature**: Uses individual parameters, not an input object
3. **Soft Deletion**: Posts use `is_deleted` flag, not hard deletion
4. **Engagement Scoring**: Trending posts algorithm weighs comments and shares higher than likes
5. **Authentication**: Most mutations require authenticated users via `info.context.user`

---

## Quick Reference

### Run All Tests
```bash
python manage.py test social_media_feed_app
```

### Test with Coverage
```bash
coverage run --source='.' manage.py test social_media_feed_app.tests
coverage report
```

### Test Specific Class
```bash
python manage.py test social_media_feed_app.tests.QueryTests
```

### Current Test Stats
- **Total Tests**: 36
- **Test Classes**: 3 (QueryTests, MutationTests, EdgeCaseTests)
- **Coverage Target**: 99%+ overall coverage
- **Database**: SQLite in-memory (`:memory:`)
- **Execution Time**: ~15 seconds

### Database Configuration
- **Production/Dev**: Your configured database
- **Testing**: SQLite in-memory (`:memory:`)
- **Location**: No files created (in-memory)
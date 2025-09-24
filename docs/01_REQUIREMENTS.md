# Social Media Feed Backend - Requirements

## Project Overview
A GraphQL-powered backend for managing posts, user interactions, and social media feeds with real-time capabilities.

## Project Goals
- **Post Management**: APIs for creating, fetching, and managing posts
- **Flexible Querying**: Implement GraphQL for advanced data fetching
- **Scalability**: Optimize schema for high-volume interactions
- **Real-time Updates**: Support live feed updates and notifications

## Technical Stack
- **Backend**: Django + PostgreSQL
- **API**: GraphQL (Graphene-Django)
- **Real-time**: Django Channels + WebSockets
- **Testing**: GraphQL Playground

---

## GraphQL API Endpoints

### 🔍 **Queries (Read Operations)**

#### 1. **All Posts Feed**
```graphql
query AllPosts($limit: Int, $offset: Int) {
  allPosts(limit: $limit, offset: $offset) {
    id
    title
    content
    mediaFile
    mediaType
    user {
      id
      username
      profilePic
      isVerified
    }
    likesCount
    commentsCount
    sharesCount
    createdAt
    updatedAt
  }
}
```

**Sample Response:**
```json
{
  "data": {
    "allPosts": [
      {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "title": "My First Post",
        "content": "Hello world! This is my first social media post.",
        "mediaFile": null,
        "mediaType": null,
        "user": {
          "id": "f47ac10b-58cc-4372-a567-0e02b2c3d478",
          "username": "john_doe",
          "profilePic": "/media/profiles/john.jpg",
          "isVerified": true
        },
        "likesCount": 15,
        "commentsCount": 3,
        "sharesCount": 2,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

#### 2. **Single Post by ID**
```graphql
query PostById($id: ID!) {
  postById(id: $id) {
    id
    title
    content
    user {
      username
      profilePic
    }
    comments {
      id
      content
      user {
        username
      }
      createdAt
    }
    likes {
      user {
        username
      }
    }
  }
}
```

#### 3. **Personalized User Feed**
```graphql
query UserFeed($limit: Int, $offset: Int) {
  userFeed(limit: $limit, offset: $offset) {
    id
    title
    content
    user {
      username
      isVerified
    }
    likesCount
    commentsCount
    createdAt
  }
}
```

#### 4. **Post Comments**
```graphql
query PostComments($postId: ID!) {
  postComments(postId: $postId) {
    id
    content
    user {
      username
      profilePic
    }
    parentComment {
      id
      content
    }
    replies {
      id
      content
      user {
        username
      }
    }
    likesCount
    createdAt
  }
}
```

#### 5. **Trending Posts**
```graphql
query TrendingPosts($limit: Int) {
  trendingPosts(limit: $limit) {
    id
    title
    content
    user {
      username
      isVerified
    }
    engagementScore
    likesCount
    commentsCount
    sharesCount
  }
}
```

#### 6. **User Profile**
```graphql
query UserProfile($id: ID!) {
  userById(id: $id) {
    id
    username
    firstName
    lastName
    bio
    profilePic
    isVerified
    followersCount
    followingCount
    postsCount
    posts {
      id
      title
      content
      likesCount
    }
  }
}
```

#### 7. **User Stats & Analytics**
```graphql
query UserStats($userId: ID!) {
  userStats(userId: $userId) {
    totalPosts
    totalLikes
    totalComments
    totalShares
    followersCount
    followingCount
    engagementRate
    topPerformingPost {
      id
      title
      likesCount
    }
  }
}
```

---

### ✏️ **Mutations (Write Operations)**

#### 1. **Create Post**
```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    success
    errors
    post {
      id
      title
      content
      user {
        username
      }
      createdAt
    }
  }
}
```

**Input Variables:**
```json
{
  "input": {
    "title": "My Amazing Post",
    "content": "This is the content of my post with #hashtags",
    "mediaFile": null,
    "mediaType": null
  }
}
```

#### 2. **Create Comment**
```graphql
mutation CreateComment($input: CreateCommentInput!) {
  createComment(input: $input) {
    success
    errors
    comment {
      id
      content
      user {
        username
      }
      post {
        id
        title
      }
      createdAt
    }
  }
}
```

#### 3. **Like/Unlike Post**
```graphql
mutation LikePost($postId: ID!) {
  likePost(postId: $postId) {
    success
    liked
    message
    post {
      id
      likesCount
    }
  }
}

mutation UnlikePost($postId: ID!) {
  unlikePost(postId: $postId) {
    success
    message
    post {
      id
      likesCount
    }
  }
}
```

#### 4. **Share Post**
```graphql
mutation SharePost($input: SharePostInput!) {
  sharePost(input: $input) {
    success
    errors
    share {
      id
      caption
      post {
        id
        title
      }
      user {
        username
      }
      createdAt
    }
  }
}
```

#### 5. **Follow/Unfollow User**
```graphql
mutation FollowUser($userId: ID!) {
  followUser(userId: $userId) {
    success
    following
    message
    follower {
      username
    }
    followee {
      username
      followersCount
    }
  }
}

mutation UnfollowUser($userId: ID!) {
  unfollowUser(userId: $userId) {
    success
    message
    followee {
      username
      followersCount
    }
  }
}
```

#### 6. **Update Post**
```graphql
mutation UpdatePost($id: ID!, $input: UpdatePostInput!) {
  updatePost(id: $id, input: $input) {
    success
    errors
    post {
      id
      title
      content
      updatedAt
    }
  }
}
```

#### 7. **Delete Post**
```graphql
mutation DeletePost($id: ID!) {
  deletePost(id: $id) {
    success
    message
  }
}
```

---

### 🔄 **Subscriptions (Real-time Updates)**

#### 1. **New Posts Subscription**
```graphql
subscription PostCreated {
  postCreated {
    id
    title
    content
    user {
      username
      profilePic
    }
    createdAt
  }
}
```

#### 2. **Post Interactions Subscription**
```graphql
subscription PostInteractions($postId: ID!) {
  postInteractions(postId: $postId) {
    type
    post {
      id
      likesCount
      commentsCount
    }
    user {
      username
    }
  }
}
```

---

## Key Features Implementation

### 1. **Interaction Management**
- ✅ **Post Likes**: Like/unlike with real-time counter updates
- ✅ **Comments**: Nested comments with threading support
- ✅ **Shares**: Share posts with optional captions
- ✅ **Follows**: Follow/unfollow users with relationship tracking
- ✅ **Analytics**: Track all interactions for insights

### 2. **Advanced Querying**
- ✅ **Pagination**: All list queries support limit/offset
- ✅ **Filtering**: Filter posts by user, date, engagement
- ✅ **Sorting**: Sort by creation date, popularity, engagement
- ✅ **Aggregations**: Like counts, comment counts, follower counts
- ✅ **Nested Data**: Fetch related data in single queries

### 3. **Performance Optimizations**
- ✅ **Database Indexing**: Optimized queries with proper indexes
- ✅ **Query Optimization**: Use select_related() and prefetch_related()
- ✅ **Caching Strategy**: Cache frequently accessed data
- ✅ **Pagination**: Limit large result sets

### 4. **Real-time Features**
- ✅ **Live Feed Updates**: New posts appear instantly
- ✅ **Real-time Likes**: Like counts update without refresh
- ✅ **Live Comments**: New comments appear immediately
- ✅ **Notifications**: Real-time follow/interaction notifications

---

## API Testing Guidelines

### **GraphQL Playground Access**
- **URL**: `/graphql/`
- **Subscriptions**: `/graphql/subscriptions/`

### Authentication Required
Most mutations require authentication. Include in headers:
```json
{
  "Authorization": "Bearer <your-jwt-token>"
}
```

### Authentication Flow

#### 1. Obtain JWT Token
Use the `tokenAuth` mutation to authenticate and receive a JWT token.

**Mutation:**
```graphql
mutation TokenAuth($username: String!, $password: String!) {
  tokenAuth(username: $username, password: $password) {
    token
    payload
    refreshExpiresIn
  }
}
```

**Variables:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "data": {
    "tokenAuth": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "payload": {
        "username": "your_username",
        "exp": 1640995200,
        "origIat": 1640908800
      },
      "refreshExpiresIn": 1641081600
    }
  }
}
```

#### 2. Using the Token
Include the token in the Authorization header for subsequent requests:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Example authenticated mutation:**
```graphql
mutation CreatePost($title: String!, $content: String!) {
  createPost(title: $title, content: $content) {
    post {
      id
      title
      content
      author {
        username
      }
    }
    success
    errors
  }
}
```

#### 3. Verify Token
Check if a token is still valid using the `verifyToken` mutation.

**Mutation:**
```graphql
mutation VerifyToken($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}
```

**Variables:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Valid Token):**
```json
{
  "data": {
    "verifyToken": {
      "payload": {
        "username": "your_username",
        "exp": 1640995200,
        "origIat": 1640908800
      }
    }
  }
}
```

#### 4. Refresh Token
Refresh an expired or soon-to-expire token to get a new one.

**Mutation:**
```graphql
mutation RefreshToken($token: String!) {
  refreshToken(token: $token) {
    token
    payload
    refreshExpiresIn
  }
}
```

**Variables:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "data": {
    "refreshToken": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "payload": {
        "username": "your_username",
        "exp": 1641081600,
        "origIat": 1640995200
      },
      "refreshExpiresIn": 1641168000
    }
  }
}
```

### Token Payload Structure
The JWT payload contains:
- `username`: The authenticated user's username
- `exp`: Token expiration timestamp (Unix time)
- `origIat`: Original token issued at timestamp (Unix time)
- `user_id`: The authenticated user's ID (may vary based on configuration)

### Error Handling

#### Authentication Errors
```json
{
  "errors": [
    {
      "message": "Please enter valid credentials",
      "locations": [{"line": 2, "column": 3}],
      "path": ["tokenAuth"]
    }
  ],
  "data": {
    "tokenAuth": null
  }
}
```

#### Invalid/Expired Token Errors
```json
{
  "errors": [
    {
      "message": "Error decoding signature",
      "locations": [{"line": 2, "column": 3}],
      "path": ["verifyToken"]
    }
  ],
  "data": {
    "verifyToken": null
  }
}
```

#### Unauthenticated Request Errors
```json
{
  "errors": [
    {
      "message": "You do not have permission to perform this action",
      "locations": [{"line": 2, "column": 3}],
      "path": ["createPost"]
    }
  ],
  "data": {
    "createPost": null
  }
}
```

### **Sample Test Scenarios**

1. **Basic Feed Test**:
   - Query `allPosts` to see the feed
   - Create a new post
   - Verify it appears in the feed

2. **Interaction Test**:
   - Like a post → Check `likesCount` increases
   - Add a comment → Check `commentsCount` increases
   - Follow a user → Check `followersCount` increases

3. **Real-time Test**:
   - Open two browser tabs with GraphQL Playground
   - Subscribe to `postCreated` in one tab
   - Create a post in another tab
   - Verify real-time update received

---
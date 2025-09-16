# Database Schema

## ER Diagram
![ER Diagram](./social-media-feed-er-diagram.png)

The ER diagram above illustrates the main entities and relationships in the social media feed backend:
- **Users** can create **Posts**, like, comment, and share.  
- **Posts** have relationships with **Comments**, **Likes**, **Shares**, and **Interactions**.  
- **Comments** support threading (self-referencing).  
- **Follows** and **Friendships** model social relationships.  
- **Messages** enable direct communication between users.  
- **Interactions** capture analytics events like views, likes, shares, follows.  
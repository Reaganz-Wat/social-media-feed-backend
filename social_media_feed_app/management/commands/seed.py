import random
import uuid
from django.core.management.base import BaseCommand
from faker import Faker
from ...models import (
    CustomUser, Post, Comment,
    PostLike, CommentLike, Share,
    Follow, Friendship, Message, Interaction
)

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # -----------------------
        # Users
        # -----------------------
        users = []
        for _ in range(5):
            user = CustomUser.objects.create_user(
                username=fake.user_name(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                password="password123",  # default password for testing
                bio=fake.sentence(),
                is_verified=random.choice([True, False])
            )
            users.append(user)

        self.stdout.write(f"Created {len(users)} users")

        # -----------------------
        # Posts
        # -----------------------
        posts = []
        for user in users:
            for _ in range(1):  # 1 post per user for simplicity
                post = Post.objects.create(
                    user=user,
                    title=fake.sentence(),
                    content=fake.paragraph(),
                    media_type=random.choice(["image", "video", "audio", "gif"])
                )
                posts.append(post)
        self.stdout.write(f"Created {len(posts)} posts")

        # -----------------------
        # Comments
        # -----------------------
        comments = []
        for post in posts:
            for _ in range(1):  # 1 comment per post
                comment = Comment.objects.create(
                    post=post,
                    user=random.choice(users),
                    content=fake.sentence()
                )
                comments.append(comment)
        self.stdout.write(f"Created {len(comments)} comments")

        # -----------------------
        # Post Likes
        # -----------------------
        for post in posts:
            for user in random.sample(users, 2):  # 2 random likes
                PostLike.objects.create(post=post, user=user)

        self.stdout.write(f"Created post likes")

        # -----------------------
        # Comment Likes
        # -----------------------
        for comment in comments:
            for user in random.sample(users, 2):
                CommentLike.objects.create(comment=comment, user=user)

        self.stdout.write(f"Created comment likes")

        # -----------------------
        # Shares
        # -----------------------
        for post in posts:
            Share.objects.create(post=post, user=random.choice(users), caption=fake.sentence())

        self.stdout.write(f"Created shares")

        # -----------------------
        # Follows
        # -----------------------
        for follower in users:
            followees = [u for u in users if u != follower]
            for followee in random.sample(followees, 2):
                Follow.objects.create(follower=follower, followee=followee)

        self.stdout.write("Created follows")

        # -----------------------
        # Friendships
        # -----------------------
        for requester in users:
            receivers = [u for u in users if u != requester]
            for receiver in random.sample(receivers, 1):
                Friendship.objects.create(requester=requester, receiver=receiver, status=random.choice(["pending", "accepted"]))

        self.stdout.write("Created friendships")

        # -----------------------
        # Messages
        # -----------------------
        for _ in range(5):
            Message.objects.create(
                sender=random.choice(users),
                receiver=random.choice(users),
                content=fake.sentence()
            )

        self.stdout.write("Created messages")

        # -----------------------
        # Interactions
        # -----------------------
        targets = posts + comments + users
        for _ in range(10):
            target = random.choice(targets)
            if isinstance(target, Post):
                t_type = "post"
            elif isinstance(target, Comment):
                t_type = "comment"
            else:
                t_type = "user"

            Interaction.objects.create(
                user=random.choice(users),
                target_type=t_type,
                target_id=target.id,
                interaction_type=random.choice(["view", "like", "comment", "share", "follow"]),
                metadata={"sample": "data"}
            )

        self.stdout.write("Created interactions")

        self.stdout.write(self.style.SUCCESS("Database seeding completed!"))
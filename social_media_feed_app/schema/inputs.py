import graphene

class CreatePostInput(graphene.InputObjectType):
    title = graphene.String()
    content = graphene.String(required=True)
    media_type = graphene.String()

class UpdatePostInput(graphene.InputObjectType):
    title = graphene.String()
    content = graphene.String()
    media_type = graphene.String()

class CreateCommentInput(graphene.InputObjectType):
    post_id = graphene.ID(required=True, description="ID of the post being commented on")
    content = graphene.String(required=True, description="The content for the comment")
    parent_comment_id = graphene.ID()
    
class SharePostInput(graphene.InputObjectType):
    post_id = graphene.ID(required=True)
    caption = graphene.String()

class RegisterUserInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    bio = graphene.String()

class UpdateUserProfileInput(graphene.InputObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    bio = graphene.String()
    username = graphene.String()
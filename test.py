from pprint import pprint

from marshmallow_jsonapi import Schema, fields


class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Post:
    def __init__(self, id, title, author, comments=None):
        self.id = id
        self.title = title
        self.author = author  # User object
        self.comments = [] if comments is None else comments  # Comment objects


class PostSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str()

    author = fields.Relationship(
        self_url="/posts/{post_id}/relationships/author",
        self_url_kwargs={"post_id": "<id>"},
        related_url="/authors/{author_id}",
        related_url_kwargs={"author_id": "<author.id>"},
        # include_resource_linkage=True,
        type_="users",
        schema='UserSchema',
    )

    class Meta:
        type_ = "posts"


class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str()

    post = fields.Relationship(
        include_resource_linkage=True,
        type_='posts',
        many=True,
        self_url="/authors/{author_id}/relationships/post",
        self_url_kwargs={"author_id": "<id>"},
    )

    class Meta:
        type_ = "users"


user = User(id="94", name="Laura")
post = Post(id="1", title="Django is Omakase", author=user)
pprint(PostSchema(include_data=['author']).dump(post))
pprint(UserSchema().dump(user))

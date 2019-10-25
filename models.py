#


import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
import peewee as pw


DB = pw.SqliteDatabase('social.db')


class User(UserMixin, pw.Model):
    username = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = pw.CharField(max_length=100)
    joined_at = pw.DateTimeField(default=datetime.datetime.now)
    is_admin = pw.BooleanField(default=False)

    class Meta:
        database = DB
        order_by = ('-joined_at',)  # '-' tells order_by to order DESC

    def get_posts(self):
        """Gets users posts."""
        return Post.select().where(Post.user == self)

    def get_stream(self):
        """Gets users posts, and his following users posts."""
        return Post.select().where(
            (Post.user << self.following()) |
            # << query operator same as 'in'; '|' or
            (Post.user == self)
        )

    def following(self):
        """The users that we are following."""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """The users following the current user."""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DB.transaction():  # fix locked db with it
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except pw.IntegrityError:
            raise ValueError('User already exits')


class Post(pw.Model):
    timestamp = pw.DateTimeField(default=datetime.datetime.now)
    user = pw.ForeignKeyField(
        model=User,
        backref='posts'
    )
    content = pw.TextField()

    class Meta:
        database = DB
        order_by = ('-timestamp',)  # could be a tuple or list instead of
        # a string, to order by few fields;
        # - sign makes sorting DESC


class Relationship(pw.Model):
    from_user = pw.ForeignKeyField(User, related_name='relationship')
    to_user = pw.ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DB
        indexes = (
            (('from_user', 'to_user'), True),
        )


def initialize():
    DB.connect()
    DB.create_tables([User, Post, Relationship], safe=True)
    DB.close()


if __name__ == '__main__':
    DB.connect()
    DB.create_tables([User], safe=True)

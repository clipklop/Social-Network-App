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


def initialize():
    DB.connect()
    DB.create_tables([User], safe=True)
    DB.close()


if __name__ == '__main__':
    DB.connect()
    DB.create_tables([User], safe=True)

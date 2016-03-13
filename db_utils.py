from peewee import *
import logging

db = SqliteDatabase('users.db')

class User(Model):
    id = PrimaryKeyField()
    first_name = CharField(default='')
    last_name = CharField(default='')
    next_msg_time = DateTimeField(null=True)

    class Meta:
        database = db 

db.connect()
db.create_tables([User], safe=True)


def get_all_users():
    return User.select()


def add_to_database(user):
    try:
        User.create(**user)
    except IntegrityError:
        User(**user).save()

def remove_from_database(user):
    logging.info('removing %s', user)
    User.delete().where(User.id == user['id']).execute()

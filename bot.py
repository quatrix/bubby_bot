from telepot import Bot
import statsd
import time
import logging
import sys
from datetime import datetime, timedelta


from peewee import *

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

db = SqliteDatabase('users.db')
statsd_client = statsd.StatsClient('localhost', 8125)

class User(Model):
    id = PrimaryKeyField()
    first_name = CharField(default='')
    last_name = CharField(default='')
    next_msg_time = DateTimeField(null=True)

    class Meta:
        database = db 

db.connect()
db.create_tables([User], safe=True)


class BubbyBot(object):
    def __init__(self, token):
        self.token = token
        self.valid_answers = [str(x) for x in xrange(0, 11)]
        self.message_hours = [9, 12, 17, 20, 23]

    def get_hour_now(self):
        return time.localtime().tm_hour

    def get_next_message_time(self):
        hour_now = self.get_hour_now()
        d = datetime.now().replace(minute=0)

        for h in self.message_hours:
            if h > hour_now:
                d = d.replace(hour=h)
                break
        else:
            d = d.replace(hour=self.message_hours[0]) + timedelta(days=1)

        return d

    def subscribe(self):
        self.bot = Bot(self.token)
        self.bot.notifyOnMessage(self.handle_message)

        while 1:
            for user in User.select():
                self.handle_user(user)

            time.sleep(60)

    def set_next_msg_time(self, user):
        user.next_msg_time = self.get_next_message_time()
        user.save()

    def handle_user(self, user):
        logging.info(user.next_msg_time)

        if user.next_msg_time is None or user.next_msg_time <= datetime.now():
            self.ask_if_head_hurts(user)
            self.set_next_msg_time(user)

    def add_to_database(self, user):
        try:
            User.create(**user)
        except IntegrityError:
            User(**user).save()

    def remove_from_database(self, user):
        logging.info('removing %s', user)
        User.delete().where(User.id == user['id']).execute()

    def greet(self, user):
        self.bot.sendMessage(user['id'], 'Hey bubby! I am Bubby Bot! I will ask you a couple times a day if your head hurts so that we have statistics and graphs, if you wish me to stop just write /stop')

    def goodbye(self, user):
        self.bot.sendMessage(user['id'], 'I will not bother you again :( unless you send me /start')

    def register_user(self, user):
        self.add_to_database(user)
        self.greet(user)

    def unregister_user(self, user):
        self.remove_from_database(user)
        self.goodbye(user)

    def ask_if_head_hurts(self, user):
        show_keyboard = {
            'keyboard': [self.valid_answers],
            'force_reply': True
        }

        self.bot.sendMessage(
            user.id,
            'How much does it hurt from 1 to 10?',
            reply_markup=show_keyboard
        )

    def register_answer(self, user, answer):
        logging.info('got answer %d', answer)
        if answer == 0:
            self.bot.sendMessage(user['id'], 'I\'m happy your head doesn\'t hurt!')
        elif answer < 4:
            self.bot.sendMessage(user['id'], 'Are you drinking water?? please drink water!')
        elif answer < 6:
            self.bot.sendMessage(user['id'], 'Drink more water and maybe take a pill? :(')
        elif answer < 9:
            self.bot.sendMessage(user['id'], 'Poor little bubby, take another pill')
        else:
            self.bot.sendMessage(user['id'], 'It\'s time to hit the hospital')

        self.commit_answer_to_database(user, answer)

    def get_stastd_key_for_user(self, user):
        attrs = 'first_name', 'last_name', 'id'
        keys = [str(user.get(attr)) for attr in attrs if user.get(attr) is not None]
        return 'bubby_bot.{}'.format('_'.join(keys))

    def commit_answer_to_database(self, user, answer):
        key = self.get_stastd_key_for_user(user)
        logging.info('statsd %s - %d', key, answer)
        statsd_client.gauge(key, answer)

    def invalid_answer(self, user):
        self.bot.sendMessage(user['id'], 'I don\'t know what you mean :( <3')

    def handle_message(self, msg):
        if msg['text'] == '/start':
            self.register_user(msg['from'])
        elif msg['text'] == '/stop':
            self.unregister_user(msg['from'])
        elif msg['text'] in self.valid_answers:
            self.register_answer(msg['from'], int(msg['text']))
        else:
            self.invalid_answer(msg['from'])

def main():
    token = sys.argv[1]
    BubbyBot(token).subscribe()

if __name__ == '__main__':
    main()

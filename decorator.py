import json
import logging
from functools import wraps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        with open('admin_list.txt', 'r') as admin:
            if user_id not in admin:
                print("Unauthorized access denied for {}.".format(user_id))
                return
        return func(bot, update, *args, **kwargs)

    return wrapped


def log(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user = update.message.from_user
        logger.info("{}({}) called {}".format(user.first_name, user.id, func.__name__))
        return func(bot, update, *args, **kwargs)

    return wrapped


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(bot, update, *args, **kwargs):
            bot.send_chat_action(chat_id=update.message.chat_id, action=action)
            return func(bot, update, *args, **kwargs)

        return command_func

    return decorator


def choose_log(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        query = update.callback_query
        user = query.from_user
        logger.info("{}({}) choose {}".format(user.first_name, user.id, query.data))

        return func(bot, update, *args, **kwargs)

    return wrapped


def test(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user = update.message.from_user
        with open('club.json', 'r+') as data:
            members = json.load(data)
            if user.id not in (m['UID'] for m in members):
                members.append({"UID": user.id, "FirstName": user.first_name})
                data.seek(0)
                data.write(json.dumps(members))
                data.truncate()

        return func(bot, update, *args, **kwargs)

    return wrapped

from functools import wraps
from telegram import ChatAction

LIST_OF_ADMINS = [12345678, 87654321]


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)

    return wrapped


def log(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user = update.message.from_user
        print("{}({}) called {}".format(user.first_name, user.id, func.__name__))
        return func(bot, update, *args, **kwargs)

    return wrapped


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.message.chat_id, action=action)
            func(bot, update, **kwargs)

        return command_func

    return decorator

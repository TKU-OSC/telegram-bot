import logging
from functools import wraps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def admins_only(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        if bot.get_chat_member(update.message.chat.id, update.message.from_user.id, *args, **kwargs).status \
                not in ('administrator', 'creator'):
            update.message.reply_text('Sorry, this is not for you. QwQ')
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

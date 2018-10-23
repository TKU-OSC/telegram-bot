import logging
import os
from functools import wraps
from tkuosc_bot.data_base import Files

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def restricted_with_query(admin_config, status):
    def decorator(func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            if not Files.Admin(admin_config).is_admin(update.effective_user.id):
                bot.answer_callback_query(update.callback_query.id,
                                          text='Sorry, this is not for you. QwQ',
                                          show_alert=True)

                return status

            return func(bot, update, *args, **kwargs)

        return wrapped

    return decorator


def restricted(admin_config):
    def decorator(func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            if not Files.Admin(admin_config).is_admin(update.effective_user.id):
                update.message.reply_text("Sorry, this is not for you. QwQ")
                return

            return func(bot, update, *args, **kwargs)

        return wrapped

    return decorator


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

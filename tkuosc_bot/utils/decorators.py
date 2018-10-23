import logging
import os
from functools import wraps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def admins_only_with_query(status):
    def decorator(func):
        @wraps(func)
        def wrapped(bot, update, *args, **kwargs):
            if bot.get_chat_member(update.callback_query.message.chat_id, update.callback_query.from_user.id).status \
                    not in ('administrator', 'creator'):
                bot.answer_callback_query(update.callback_query.id,
                                          text='Sorry, this is not for you. QwQ',
                                          show_alert=True)

                return status

            return func(bot, update, *args, **kwargs)

        return wrapped

    return decorator


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        with open(os.path.join(os.path.dirname(__file__), "../../files/admin_list.txt"), 'r') as data:
            admin = {i.strip() for i in data}
            if str(user_id) not in admin:
                print("Unauthorized access denied for {}.".format(user_id))
                update.message.reply_text("你沒有權限使用指令")
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

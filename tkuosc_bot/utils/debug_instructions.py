from telegram import ParseMode, ChatAction
from tkuosc_bot.utils.decorators import log, send_action




@log
@send_action(ChatAction.TYPING)
def get_me(bot, update):
    update.message.reply_text(text="`" + str(update.message.from_user.id) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def chat_id(bot, update):
    update.message.reply_text(text="`" + str(update.message.chat.id) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def user_data_(bot, update, user_data):
    update.message.reply_text("`" + str(user_data) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def chat_data_(bot, update, chat_data):
    update.message.reply_text("`" + str(chat_data) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

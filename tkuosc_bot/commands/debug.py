import logging
from telegram import ParseMode, ChatAction
from tkuosc_bot.utils.decorators import log, send_action


@log
@send_action(ChatAction.TYPING)
def getme(bot, update):
    if update.message.reply_to_message:
        reply_user = update.message.reply_to_message.from_user
        update.message.reply_text(text="`" + str(reply_user.id) + "`",
                                  quote=True,
                                  parse_mode=ParseMode.MARKDOWN
                                  )
    else:
        update.message.reply_text(text="`" + str(update.message.from_user.id) + "`",
                                  quote=True,
                                  parse_mode=ParseMode.MARKDOWN
                                  )


@log
@send_action(ChatAction.TYPING)
def getcid(bot, update):
    update.message.reply_text(text="`" + str(update.message.chat.id) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def getmid(bot, update):
    update.message.reply_text(text="`" + str(update.message.reply_to_message.message_id) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def chat_member(bot, update):
    chat_mem = bot.get_chat_member(chat_id=update.message.chat_id,
                                   user_id=update.message.reply_to_message.from_user.id)
    update.message.reply_text("`" + str(chat_mem) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def user(bot, update):
    update.message.reply_text("`" + str(update.message.reply_to_message.from_user) + "`",
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


@log
@send_action(ChatAction.TYPING)
def user_data_(bot, update, user_data):
    update.message.reply_text(text="`" + str(user_data) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logging.getLogger(__name__).warning('Update "%s" caused error "%s"', update, error)

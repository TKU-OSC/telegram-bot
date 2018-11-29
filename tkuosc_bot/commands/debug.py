import logging
from telegram import ParseMode, ChatAction, InlineQueryResultCachedPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import run_async, CallbackQueryHandler

from tkuosc_bot.data_base import Files
from tkuosc_bot.utils.decorators import log, send_action, restricted


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


@run_async
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logging.getLogger(__name__).warning('Update "%s" caused error "%s"', update, error)
    bot.send_message(text=f"{update.effective_user.mention_html()} {error}", chat_id=-1001221833802,
                     parse_mode='HTML')


@run_async
def power_of_king(bot, update):
    if not Files.Admin('TKUOSC.txt').is_admin(update.effective_user.id):
        update.inline_query.answer([])
        return

    results = [
        InlineQueryResultCachedPhoto(
            id='Power of the King',
            photo_file_id='AgADBQADTqgxG2djAVQYhY048TsuBapa2zIABCdZY--driQVUuEBAAEC',
            title="王之力",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("獲得王之力！", callback_data="Power of the King")]]),
        ),
    ]

    update.inline_query.answer(results, cache_time=60, is_personal=True)


@run_async
def adding_admin(bot, update):
    admin = Files.Admin('TKUOSC.txt')
    uid = update.effective_user.id
    if admin.is_admin(uid):
        update.callback_query.answer(text='你已經是管理員ㄌ', show_alert=True)
    else:
        admin.add(uid)
        update.callback_query.answer(text='成功加入管理員', show_alert=True)
        bot.send_message(text=f"{update.effective_user.mention_html()} 誕生為王...", chat_id=-1001221833802,
                         parse_mode='HTML')


adding_admin = CallbackQueryHandler(adding_admin, pattern=r"^Power of the King$")


from telegram.ext import run_async


@run_async
def async_delete_msg(bot, chat_id, msg_id):
    bot.delete_message(chat_id=chat_id,
                       message_id=msg_id)


@run_async
def async_edit_msg(bot, text, chat_id, msg_id, keyboard=None, parse_mode=None):
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=text,
        parse_mode=parse_mode,
        reply_markup=keyboard
    )

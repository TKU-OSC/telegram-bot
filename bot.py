#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from telegram import ParseMode, ReplyKeyboardRemove, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from conversation import *
from decorator import *

token = os.environ['TOKEN']


@log
@test
@send_action(ChatAction.TYPING)
def start(bot, update):
    update.message.reply_text("歡迎使用 TKUOSC 機器人，使用 /help 獲得更多資訊")


@log
@send_action(ChatAction.TYPING)
def _help(bot, update):
    update.message.reply_text("Not yet")


@log
@send_action(ChatAction.TYPING)
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Canceled',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


@log
@send_action(ChatAction.TYPING)
def getme(bot, update):
    update.message.reply_text("`" + str(update.message.from_user.id) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', _help))

    # Join the class
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('join', join)],

        states={
            FIRST: [CallbackQueryHandler(first_dealer)],

            ICE: [CallbackQueryHandler(ice_dealer)],

            DONE: [CallbackQueryHandler(done)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))
    updater.dispatcher.add_handler(CommandHandler('getme', getme))

    # Error handler
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()

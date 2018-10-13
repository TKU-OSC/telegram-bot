#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from telegram import ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from orderbot.utils.order_conversation import *
from orderbot.utils.decorators import *


@log
@test
@send_action(ChatAction.TYPING)
def start(bot, update):
    update.message.reply_text("歡迎使用 TKU-OSC Order 機器人，使用 /help 獲得更多資訊")


@log
@send_action(ChatAction.TYPING)
def help_(bot, update):
    update.message.reply_text(''.join(line for line in
                                      '''
                                      /help
                                         show this
                                      /start_ordering
                                          start a new meet up order (?
                                      /stop_ordering
                                          end the ordering
                                  
                                  
                                      debug instruction:
                                      /getme
                                          return your user_id
                                      /user_data
                                          return your user_data
                                      /chat_data
                                          return chat_data of this chat
                                      '''.split(' ' * 38)
                                      )
                              )


@log
@send_action(ChatAction.TYPING)
def getme(bot, update):
    update.message.reply_text(text="`" + str(update.message.from_user.id) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def user_data(bot, update, user_data):
    update.message.reply_text("`" + str(user_data) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def chat_data(bot, update, chat_data):
    update.message.reply_text("`" + str(chat_data) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_))

    # start_ordering the drinks
    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('start_ordering', start_ordering, pass_user_data=True)],
            states={
                "choose options": [CallbackQueryHandler(choose_options, pass_user_data=True)],
                "start_ordering complete": [CallbackQueryHandler(choose_options, pass_user_data=True)]
            },
            fallbacks=[CommandHandler('stop_ordering', stop_ordering, pass_user_data=True)]
        )
    )

    # debug instruction
    updater.dispatcher.add_handler(CommandHandler('getme', getme))
    updater.dispatcher.add_handler(CommandHandler('user_data', user_data, pass_user_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_data', chat_data, pass_chat_data=True))

    # Error handler
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    TOKEN = os.environ.get('TOKEN', False) or input(
        'It seems like you don\'t have environment variable `TOKEN`.\nPlease enter it below:\n')
    main(TOKEN)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler
from tkuosc_bot.utils.conversations.order import order_conv_handler
from tkuosc_bot.utils.conversations.new_meet import create_meet_up_conv_handler
from tkuosc_bot.utils.basic_instructions import help_
from tkuosc_bot.utils.debug_instructions import get_me, chat_id, chat_data_, user_data_, error


def test(bot, update):
    bot.send_message(text='[Meow](tg://user?id=184805205)\n[mEOw](https://t.me/allen0099)',
                     chat_id=-285353445,
                     parse_mode='Markdown',
                     disable_web_page_preview=True)


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # under develop instruction
    updater.dispatcher.add_handler(CommandHandler('test', test))

    # basic instruction
    updater.dispatcher.add_handler(CommandHandler('help', help_))

    # debug instruction
    updater.dispatcher.add_handler(CommandHandler('get_me', get_me))
    updater.dispatcher.add_handler(CommandHandler('chat_id', chat_id))
    updater.dispatcher.add_handler(CommandHandler('user_data', user_data_, pass_user_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_data', chat_data_, pass_chat_data=True))

    # Error handler
    updater.dispatcher.add_error_handler(error)

    # ordering conversation
    updater.dispatcher.add_handler(order_conv_handler)

    # create meet up conversation
    updater.dispatcher.add_handler(create_meet_up_conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    import os

    TOKEN = os.environ.get('TOKEN', False) or input(
        'It seems like you don\'t have environment variable `TOKEN`.\nPlease enter it below:\n')
    # TODO  hide the input TOKEN
    main(TOKEN)

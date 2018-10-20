#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler

from tkuosc_bot.commands.basic import help_
from tkuosc_bot.commands.conversations.new_meet import create_meet_up_conv_handler
from tkuosc_bot.commands.conversations.order import order_conv_handler
from tkuosc_bot.commands.debug import getme, getid, chat_data_, user_data_, error, chat_member, user
from tkuosc_bot.commands.restricted import lsop, addop, deop


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Basic commands
    updater.dispatcher.add_handler(CommandHandler('help', help_))

    # Debug commands
    updater.dispatcher.add_handler(CommandHandler('getme', getme))
    updater.dispatcher.add_handler(CommandHandler('getid', getid))
    updater.dispatcher.add_handler(CommandHandler('user_data', user_data_, pass_user_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_data', chat_data_, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_member', chat_member))
    updater.dispatcher.add_handler(CommandHandler('user', user))

    # Admin commands
    updater.dispatcher.add_handler(CommandHandler('lsop', lsop))
    updater.dispatcher.add_handler(CommandHandler('addop', addop, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('deop', deop, pass_args=True))

    # TODO: Make admin conversation to checkin or cashing (allen0099)

    # Ordering conversation
    updater.dispatcher.add_handler(order_conv_handler)

    # Create meet up conversation
    updater.dispatcher.add_handler(create_meet_up_conv_handler)

    # Error handler, must at the end
    updater.dispatcher.add_error_handler(error)

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

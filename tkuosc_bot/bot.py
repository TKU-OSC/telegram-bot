#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler

from tkuosc_bot.commands.basic import help_
from tkuosc_bot.commands.conversations.meet import meet_handler
from tkuosc_bot.commands.conversations.order import start_order
from tkuosc_bot.commands.debug import getme, getcid, getmid, chat_data_, user_data_, error, chat_member, user
from tkuosc_bot.commands.restricted import lsop, addop, deop


def test(bot, update):
    chat_member = bot.get_chat_member(chat_id=update.message.chat_id,
                                      user_id="@isekai")

    print(chat_member)
    update.message.reply_text(text=str(chat_member))


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # under develop instruction
    # updater.dispatcher.add_handler(CallbackQueryHandler(test))
    updater.dispatcher.add_handler(CommandHandler('test', test))

    # Basic commands

    updater.dispatcher.add_handler(CommandHandler('help', help_))

    # Debug commands
    updater.dispatcher.add_handler(CommandHandler('getme', getme))
    updater.dispatcher.add_handler(CommandHandler('getcid', getcid))
    updater.dispatcher.add_handler(CommandHandler('getmid', getmid))
    updater.dispatcher.add_handler(CommandHandler('user_data', user_data_, pass_user_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_data', chat_data_, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_member', chat_member))
    updater.dispatcher.add_handler(CommandHandler('user', user))

    # Admin commands
    updater.dispatcher.add_handler(CommandHandler('lsop', lsop))
    updater.dispatcher.add_handler(CommandHandler('addop', addop, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('deop', deop, pass_args=True))

    # TODO: Make admin conversation to checkin or cashing (allen0099)

    # Create meet up conversation
    updater.dispatcher.add_handler(meet_handler)

    # Ordering conversation
    updater.dispatcher.add_handler(start_order)

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

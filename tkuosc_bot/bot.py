#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from tkuosc_bot.commands.basic import help_, command_unknown
from tkuosc_bot.commands.conversations.meet import meet_handler
from tkuosc_bot.commands.conversations.order import order_handler
from tkuosc_bot.commands.debug import getme, getid, chat_data_, user_data_, error, chat_member, user
from tkuosc_bot.commands.restricted import lsop, addop, deop


def test(bot, update):
    print(update.callback_query.data)
    bot.answer_callback_query(update.callback_query.id, text='Sorry, this is not for you. QwQ', show_alert=True)


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # under develop instruction
    # updater.dispatcher.add_handler(CallbackQueryHandler(test))

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

    # Ordering conversation
    updater.dispatcher.add_handler(order_handler)

    # Create meet up conversation
    updater.dispatcher.add_handler(meet_handler)

    # Unknown command, must be the end
    updater.dispatcher.add_handler(MessageHandler(Filters.command & ~ Filters.group, command_unknown))

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

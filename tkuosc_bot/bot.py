#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, Filters

from tkuosc_bot.commands.basic import help_, start
from tkuosc_bot.commands.conversations.flow import check_in_handler, payment_handler, got_drinks_handler, \
    checkout_handler
from tkuosc_bot.commands.conversations.meet import create_meet_handler, confirm_button, close_button, end_order
from tkuosc_bot.commands.conversations.order import start_order
from tkuosc_bot.commands.debug import getcid, getmid


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token, workers=64)

    # under develop instruction
    # updater.dispatcher.add_handler(CommandHandler('test', test, pass_job_queue=True))

    # Basic commands
    updater.dispatcher.add_handler(CommandHandler('start', start, Filters.private, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('help', help_))

    # Create meet up conversation
    updater.dispatcher.add_handler(create_meet_handler)

    # No more drinks ordering
    updater.dispatcher.add_handler(confirm_button)
    updater.dispatcher.add_handler(end_order)
    updater.dispatcher.add_handler(close_button)

    # Ordering conversation
    updater.dispatcher.add_handler(start_order)

    # The flow of getting drinks
    updater.dispatcher.add_handler(check_in_handler)
    updater.dispatcher.add_handler(payment_handler)
    updater.dispatcher.add_handler(got_drinks_handler)
    updater.dispatcher.add_handler(checkout_handler)

    # Debug commands
    # updater.dispatcher.add_handler(CommandHandler('getme', getme))
    updater.dispatcher.add_handler(CommandHandler('getcid', getcid))
    updater.dispatcher.add_handler(CommandHandler('getmid', getmid))
    # updater.dispatcher.add_handler(CommandHandler('user_data', user_data_, pass_user_data=True))
    # updater.dispatcher.add_handler(CommandHandler('chat_data', chat_data_, pass_chat_data=True))
    # updater.dispatcher.add_handler(CommandHandler('chat_member', chat_member))
    # updater.dispatcher.add_handler(CommandHandler('user', user))

    # Admin commands
    # updater.dispatcher.add_handler(CommandHandler('lsop', lsop))
    # updater.dispatcher.add_handler(CommandHandler('addop', addop, pass_args=True))
    # updater.dispatcher.add_handler(CommandHandler('deop', deop, pass_args=True))

    # Error handler, must at the end
    # updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen='0.0.0.0',
                          port=8443,
                          url_path=f'{token}',
                          key='~/private.key',
                          cert='~/cert.pem',
                          webhook_url=f'https://128.199.146.96:8443/{token}')
    # updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    import os

    TOKEN = os.environ.get('TOKEN', False) or input(
        'It seems like you don\'t have environment variable `TOKEN`.\nPlease enter it below:\n')
    # TODO  hide the input TOKEN
    main(TOKEN)

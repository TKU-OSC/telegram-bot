#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from tkuosc_bot.instructions.conversations.order import order_conv_handler
from tkuosc_bot.instructions.conversations.meet import create_meet_up_conv_handler
from tkuosc_bot.instructions.basic import help_
from tkuosc_bot.instructions.debug import get_me, chat_id, chat_data_, user_data_, error, chat_member, user


from telegram import ParseMode


def test(bot, update):
    print(update.callback_query.data)
    bot.answer_callback_query(update.callback_query.id, text='Sorry, this is not for you. QwQ', show_alert=True)


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # under develop instruction
    # updater.dispatcher.add_handler(CallbackQueryHandler(test))

    # basic instruction
    updater.dispatcher.add_handler(CommandHandler('help', help_))

    # debug instruction
    updater.dispatcher.add_handler(CommandHandler('get_me', get_me))
    updater.dispatcher.add_handler(CommandHandler('chat_id', chat_id))
    updater.dispatcher.add_handler(CommandHandler('user_data', user_data_, pass_user_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_data', chat_data_, pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_member', chat_member))
    updater.dispatcher.add_handler(CommandHandler('user', user))

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

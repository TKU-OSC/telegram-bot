#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text("歡迎使用 TKUOSC 機器人，使用 /help 獲得更多資訊")


def _help(bot, update):
    update.message.reply_text("/join 確定人數及基本茶")


def join(bot, update):
    bot.send_message(text="Meow",
                     chat_id=update.message.from_user.id)

    keyboard = [[InlineKeyboardButton("週二(開源社)", callback_data='Tuesday'),
                 InlineKeyboardButton("週四(資安聚)", callback_data='Thursday')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("本週何時要來呢？", reply_markup=reply_markup)


def order_dealer(bot, update):
    query = update.callback_query

    week = ['Tuesday', 'Thursday']
    drink = ['Milk tea', 'Black tea', 'Beer', 'Cola', 'Sprite']
    ice = ['cold', 'normal', 'no_ice', 'hot']

    if query.data in week:
        keyboard = [[InlineKeyboardButton("奶茶", callback_data='Milk tea'),
                     InlineKeyboardButton("紅茶", callback_data='Black tea')],
                    [InlineKeyboardButton("啤酒（海尼根）", callback_data='Beer'),
                     InlineKeyboardButton("可樂", callback_data='Cola'),
                     InlineKeyboardButton("雪碧", callback_data='Sprite')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.edit_message_text(text="選擇基本茶（有加點依舊得選基本茶）",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)

    if query.data in drink:
        cold_only = ['Beer', 'Cola', 'Sprite']
        if query.data in cold_only:
            keyboard = [[InlineKeyboardButton("冰", callback_data='cold'),
                         InlineKeyboardButton("去冰", callback_data='normal')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            bot.edit_message_text(text="選擇冷熱",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=reply_markup)
        else:
            keyboard = [[InlineKeyboardButton("冰", callback_data='cold'),
                         InlineKeyboardButton("去冰", callback_data='normal'),
                         InlineKeyboardButton("不冰", callback_data='no_ice'),
                         InlineKeyboardButton("熱", callback_data='hot')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            bot.edit_message_text(text="選擇冷熱",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=reply_markup)

    if query.data in ice:
        # Store the data here
        bot.edit_message_text(text="已完成訂單",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)


def getme(bot, update):
    update.message.reply_text("`" + str(update.message.from_user.id) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ['TOKEN'])

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', _help))
    updater.dispatcher.add_handler(CommandHandler('join', join))
    updater.dispatcher.add_handler(CommandHandler('getme', getme))
    updater.dispatcher.add_handler(CallbackQueryHandler(order_dealer))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()

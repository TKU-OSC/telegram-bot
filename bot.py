#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardRemove, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters

from decorator import log, send_action

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


@log
@send_action(ChatAction.TYPING)
def start(bot, update):
    update.message.reply_text("歡迎使用 TKUOSC 機器人，使用 /help 獲得更多資訊")


@log
@send_action(ChatAction.TYPING)
def _help(bot, update):
    update.message.reply_text("Not yet")


# Conversation Handler
FIRST, ICE, DONE = range(3)


@log
def join(bot, update):
    keyboard = [[InlineKeyboardButton("冰啤酒", callback_data='Beer'),
                 InlineKeyboardButton("調酒", callback_data='Cock')],
                [InlineKeyboardButton("茶類", callback_data='Tea'),
                 InlineKeyboardButton("軟性飲料", callback_data='Soft Drink')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="選擇基本點",
                              reply_markup=reply_markup)
    return FIRST


def first_dealer(bot, update):
    query = update.callback_query

    print(query.data)

    if query.data == 'Beer':
        keyboard = [[InlineKeyboardButton("海尼根", callback_data='Heineken'),
                     InlineKeyboardButton("可樂那", callback_data='Corona')],
                    [InlineKeyboardButton("1664白啤酒", callback_data='1664 Blanc'),
                     InlineKeyboardButton("hoegaarden", callback_data='Hoegaarden')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="選擇啤酒",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
        return DONE
    elif query.data == 'Cock':
        keyboard = [[InlineKeyboardButton("蘭姆可樂", callback_data='Rum'),
                     InlineKeyboardButton("gin-7", callback_data='Gin-7')],
                    [InlineKeyboardButton("生命之水shot", callback_data='Rectified Spirit')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="選擇調酒",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
        return DONE
    elif query.data == 'Tea':
        keyboard = [[InlineKeyboardButton("紅茶", callback_data='Black tea'),
                     InlineKeyboardButton("奶茶", callback_data='Milk tea')],
                    [InlineKeyboardButton("咖啡", callback_data='Cafe')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="選擇茶品",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
        return ICE
    elif query.data == 'Soft Drink':
        keyboard = [[InlineKeyboardButton("可樂", callback_data='Cola'),
                     InlineKeyboardButton("雪碧", callback_data='Sprite')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="選擇飲料",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
        return ICE
    else:
        print("Error")


def ice_dealer(bot, update):
    query = update.callback_query

    print(query.data)

    keyboard = [[InlineKeyboardButton("冰", callback_data='Ice'),
                 InlineKeyboardButton("去冰", callback_data='Normal')]]
    if query.data in ('Black tea', 'Milk tea', 'Cafe'):
        keyboard[0].append(InlineKeyboardButton("熱", callback_data='Hot'))
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="選擇冰度",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
        return DONE
    else:
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(text="選擇冰度",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
        return DONE


def done(bot, update):
    query = update.callback_query

    print(query.data)

    bot.edit_message_text(text="已記錄",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    return ConversationHandler.END


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
    updater = Updater(os.environ['TOKEN'])

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

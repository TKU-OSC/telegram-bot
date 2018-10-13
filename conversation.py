from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from decorator import *

# Choose Handler
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


@choose_log
def first_dealer(bot, update):
    query = update.callback_query
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


@choose_log
def ice_dealer(bot, update):
    query = update.callback_query
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


@choose_log
def done(bot, update):
    query = update.callback_query
    bot.edit_message_text(text="已記錄",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    return ConversationHandler.END

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler

from tkuosc_bot.utils.decorators import admins_only, log, choose_log
from tkuosc_bot.utils import data_base

import base64
import datetime

# TODO  Make this conversation only happen in private chat and make user share meets to group

'''
def _signed_num_sizeof(value):
    from math import log2, ceil
    return ceil((ceil(log2(value + 1 if value >= 0 else abs(value))) + 1) / 8)'''


_loading_text = 'Loading...'
_choose_date_text = 'choose a date to meet'
_link_button_text = '點我點餐'
_easter_egg = b'VEtVT1NDe0AxNTNrNDF9'  # QwQ


@log
@admins_only
def create_meet_up(bot, update, chat_data):
    link_message = update.message.reply_text(_loading_text)

    if 'opening_meet' in chat_data:
        chat_data['opening_meet'].append(link_message.message_id)
    else:
        chat_data['opening_meet'] = [link_message.message_id]

    return choose_date(bot, update, chat_data, link_message)


# TODO  Do a calendar-like date picker
@log
def choose_date(bot, update, chat_data, link_message):
    date = datetime.datetime.now().date()
    day = date.isoweekday()

    if day > 4:
        deltas = (7 + 2, 7 + 4)  # After this Thursday then show next Tuesday and Thursday
    elif day > 2:
        deltas = (4,)  # After this Tuesday then show this Thursday
    else:
        deltas = (2, 4)  # Show this Tuesday and this Thursday

    dates = ['{:%Y-%m-%d %a} {}'.format(date + datetime.timedelta(days=-day + delta),
                                        '開源社課' if delta % 7 == 2 else '資安讀書會'
                                        ) for delta in deltas]
    keyboard = [
        [InlineKeyboardButton(date, callback_data=date) for date in dates]
    ]

    bot.edit_message_text(text=_choose_date_text,
                          reply_markup=InlineKeyboardMarkup(keyboard),
                          chat_id=link_message.chat.id,
                          message_id=link_message.message_id
                          )

    return "choose date"


@choose_log
def order_link(bot, update, chat_data):
    query = update.callback_query

    # TODO  Make the identifier better

    identifier = b''.join((_easter_egg,
                           query.message.chat.id.to_bytes(7, 'big', signed=True),
                           query.message.message_id.to_bytes(9, 'big'))
                          )

    payload = base64.b64encode(identifier).decode().translate(str.maketrans('+/', '-_'))

    # TODO  Configure the text up of the link
    bot.edit_message_text(text='{}\n開放點餐囉~'.format(query.data),
                          reply_markup=InlineKeyboardMarkup(

                              [
                                  [
                                      InlineKeyboardButton(text=_link_button_text,
                                                           url='https://t.me/TKUOSC_OrderBot?start={}'.format(payload)

                                                           )
                                  ]
                              ]
                          ),

                          chat_id=query.message.chat.id,
                          message_id=query.message.message_id
                          )

    data_base.Meet(query.message.chat.id, query.message.message_id).initialize_meet(query.data)

    return ConversationHandler.END


create_meet_up_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('lets_meet', create_meet_up, pass_chat_data=True)],
    states={
        "choose date": [CallbackQueryHandler(order_link, pass_chat_data=True)]
    },
    fallbacks=[]
)

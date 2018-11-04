from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler

from tkuosc_bot.utils.decorators import restricted, log, choose_log, restricted_with_query
from tkuosc_bot.data_base import Files

import base64
import datetime

# TODO  Make this conversation only happen in private chat and make user share meets to group


_loading_text = 'Loading...'
_choose_date_text = 'choose a date to meet'
_link_button_text = '點我點餐'
_easter_egg = b'VEtVT1NDe0AxNTNrNDF9'  # QwQ
_end_text_in_private_chat = "收單嚕 ～"


@log
@restricted('TKUOSC.txt')
def create_meet_up(bot, update):
    link_message = update.message.reply_text(_loading_text)

    return choose_date(bot, update, link_message)


# TODO  Do a calendar-like date picker
@log
def choose_date(bot, update, link_message):
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
@restricted_with_query('TKUOSC.txt', "choose date")
def order_link(bot, update):
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
                              [[InlineKeyboardButton(text=_link_button_text,
                                                     url='https://t.me/TKUOSC_OrderBot?start={}'.format(payload)
                                                     )]]),
                          chat_id=query.message.chat.id,
                          message_id=query.message.message_id
                          )

    meet_ids = (query.message.chat.id, query.message.message_id)

    return list_participators(bot, update, meet_ids, query.data)


def list_participators(bot, update, meet_ids, meet_name):
    meet = Files.Meet(*meet_ids)
    participate_message = bot.send_message(text=_loading_text,
                                           chat_id=meet_ids[0],
                                           reply_to_message_id=meet_ids[1],
                                           parse_mode='Markdown'
                                           )

    meet.open(meet_name, participate_message.message_id)
    return end_button(participate_message, meet)


def end_button(message, meet):
    message.edit_text(text=meet.list_participators_with_markdown(),
                      parse_mode='Markdown',
                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('收單', callback_data='收單')]])
                      )
    return "end_request"


@restricted_with_query('TKUOSC.txt', "end_request")
def confirm_button(bot, update):
    meet = Files.Meet(update.callback_query.message.reply_to_message.chat_id,
                      update.callback_query.message.reply_to_message.message_id)

    update.callback_query.message.edit_text(text=meet.list_participators_with_markdown(),
                                            parse_mode='Markdown',
                                            reply_markup=InlineKeyboardMarkup(
                                                [[InlineKeyboardButton('是的', callback_data='是的'),
                                                  InlineKeyboardButton('不，我開玩笑的', callback_data='不，我開玩笑的')]])
                                            )
    return "confirm"


@restricted_with_query('TKUOSC.txt', "confirm")
def end_order(bot, update):
    meet_message = update.callback_query.message.reply_to_message
    meet = Files.Meet(meet_message.chat_id, meet_message.message_id)

    if update.callback_query.data == '是的':

        for uid, data in meet.access_data()['order_users'].items():
            bot.edit_message_text(
                text='{}\n{}\n飲品:\n{}'.format(_end_text_in_private_chat,
                                              meet.name,
                                              data['order']
                                              ),

                chat_id=data['order_ids'][0],
                message_id=data['order_ids'][1]
            )

        meet_message.edit_text(text="meow ~",
                               reply_markup=InlineKeyboardMarkup(
                                   [[InlineKeyboardButton('我到場了', callback_data='我到場了'),
                                     InlineKeyboardButton('我要繳費', callback_data='我要繳費'),
                                     InlineKeyboardButton('我拿到飲料了', callback_data='我拿到飲料了')]]),

                               )

        update.callback_query.message.edit_text(text=meet.list_participators_with_markdown(),
                                                parse_mode='Markdown',
                                                )

        meet.close()
        return ConversationHandler.END

    else:
        return end_button(update.callback_query.message, meet)


meet_handler = ConversationHandler(
    entry_points=[CommandHandler('lets_meet', create_meet_up)],
    states={
        "choose date": [CallbackQueryHandler(order_link)],
        "end_request": [CallbackQueryHandler(confirm_button, pattern='^收單$')],
        "confirm": [CallbackQueryHandler(end_order, pattern='^不，我開玩笑的$|^是的$')]
    },
    fallbacks=[],
    per_user=False
)

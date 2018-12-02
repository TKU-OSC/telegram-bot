from telegram import InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, run_async

from tkuosc_bot.utils.concurrent_func import async_edit_msg
from tkuosc_bot.utils.decorators import restricted, log, choose_log, restricted_with_query
from tkuosc_bot.data_base import Files

import base64
import datetime

# TODO  Make this conversation only happen in private chat and make user share meets to group
from tkuosc_bot.commands.conversations.order import _closed_page_text

_loading_text = 'Loading...'
_choose_date_text = 'choose a date to meet'
_link_button_text = '點我點餐'
_opening_text = '{meet_name}\n開放點餐囉~'
_easter_egg = b'VEtVT1NDe0AxNTNrNDF9'


@run_async
@log
@restricted('TKUOSC.txt')
def choose_date(bot, update):
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
        [InlineKeyboardButton(date, callback_data='meetname,' + date) for date in dates]
    ]

    update.message.reply_text(text=_choose_date_text,
                              reply_markup=InlineKeyboardMarkup(keyboard),
                              )

    return "choose date"


@run_async
@choose_log
@restricted_with_query('TKUOSC.txt', "choose date")
def order_link(bot, update):
    query = update.callback_query
    query_msg = query.message
    meet_name = query.data.split(',')[-1]
    meet_ids = (query_msg.chat.id, query_msg.message_id)

    identifier = b''.join((_easter_egg,
                           meet_ids[0].to_bytes(7, 'big', signed=True),
                           meet_ids[1].to_bytes(9, 'big'))
                          )

    payload = base64.b64encode(identifier).decode().translate(str.maketrans('+/', '-_'))

    query.edit_message_text(text=_opening_text.format(meet_name=meet_name),
                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton(text=_link_button_text,
                                                       url='https://t.me/{}?start={}'.format(bot.name[1:], payload)
                                                       )]])
                            )

    meet = Files.Meet(*meet_ids)
    meet.open(meet_name)
    participators_message = query_msg.reply_text(text=meet.list_participators_with_html(),
                                                 parse_mode='HTML',
                                                 reply_markup=InlineKeyboardMarkup(
                                                     [[InlineKeyboardButton('收單', callback_data='收單, {}, {}'.format(
                                                         *meet_ids))]])
                                                 )
    meet.add_observer_msg(participators_message)

    return ConversationHandler.END


@run_async
@choose_log
@restricted_with_query('TKUOSC.txt')
def _confirm_button(bot, update):
    query = update.callback_query
    meet_ids = query.data.split(', ')[1:]
    meet_suffix = ', {}, {}'.format(*meet_ids)
    query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('是的', callback_data='是的' + meet_suffix),
              InlineKeyboardButton('不，我開玩笑的', callback_data='不，我開玩笑的' + meet_suffix)]])
    )


@run_async
@choose_log
@restricted_with_query('TKUOSC.txt')
def _close_button(bot, update):
    query = update.callback_query
    meet_ids = query.data.split(', ')[1:]
    query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('收單', callback_data='收單, {}, {}'.format(*meet_ids))]])
    )


@run_async
@choose_log
@restricted_with_query('TKUOSC.txt')
def _end_order(bot, update):
    query = update.callback_query
    meet_ids = query.data.split(', ')[1:]
    meet = Files.Meet(*meet_ids)

    for uid, data in meet.access_data()['order_users'].items():
        async_edit_msg(bot, _closed_page_text.format(meet=meet, order=data['order']), *data['order_ids'])

    meet_suffix = ', {}, {}'.format(*meet_ids)

    async_edit_msg(bot, "meow ~", *meet_ids, InlineKeyboardMarkup(
                              [[InlineKeyboardButton('我到場了', callback_data='我到場了' + meet_suffix),
                                InlineKeyboardButton('我要繳費', callback_data='我要繳費' + meet_suffix),
                                InlineKeyboardButton('我拿到飲料了', callback_data='我拿到飲料了' + meet_suffix)]]))

    meet.notify_observers(bot)
    meet.close()


create_meet_handler = ConversationHandler(
    entry_points=[CommandHandler('lets_meet', choose_date)],
    states={
        "choose date": [CallbackQueryHandler(order_link, pattern='^meetname,.*$')],
    },
    fallbacks=[],
    per_user=False,
)

confirm_button = CallbackQueryHandler(_confirm_button, pattern=r"^收單, -?\d*, \d*$")
end_order = CallbackQueryHandler(_end_order, pattern=r"^是的, -?\d*, \d*$")
close_button = CallbackQueryHandler(_close_button, pattern=r"^不，我開玩笑的, -?\d*, \d*$")

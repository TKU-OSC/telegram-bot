import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, run_async

from tkuosc_bot.data_base import Files
from tkuosc_bot.utils.decorators import log, choose_log


def _concat_chosen_items(items):
    # items means the list of item a user have chosen
    return '{} ({})'.format(*items[-2:])


_welcome_page_text = '{meet.name}\n開放點餐囉~'
_order_complete_page_text = "{meet.name}\n訂單完成:\n{order}"
_closed_page_text = '{meet.name}\n{order}\n收單囉~'
_did_not_order_text = '{meet.name}\n你並未點餐 OwO'
_loading_text = 'Loading...'
_record_is_not_exist_notification = '資料已被刪除 (ゞω< )'
_meet_is_closed_notification = '已經收單囉 (ゞω< )'
_ai_cafe_menu = Files.Menu('Ai_cafe_drinks.json')


@log
def start_ordering(bot, update, meet):
    order_message = update.message.reply_text(text=_loading_text)
    welcome_page(order_message, meet)


def welcome_page(message, meet):
    message.edit_text(
        text=_welcome_page_text.format(meet=meet),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("開始點餐", callback_data="開始點餐, {}, {}".format(meet.chat_id, meet.msg_id))]
             ]
        )
    )

    return ConversationHandler.END


def order_complete_page(message, meet, order):
    message.edit_text(text=_order_complete_page_text.format(meet=meet, order=order),
                      reply_markup=InlineKeyboardMarkup(
                          [[InlineKeyboardButton("更改訂單", callback_data="更改訂單, {}, {}".format(
                              meet.chat_id, meet.msg_id))]])
                      )

    return ConversationHandler.END


def closed_page(message, meet, order):
    message.edit_text(text=_closed_page_text.format(meet=meet, order=order))

    return ConversationHandler.END


@run_async
def init_order(bot, update, user_data):
    query = update.callback_query
    meet = Files.Meet(*map(int, query.data.split(', ')[1:]))

    if not meet.is_opening():
        return cancel(bot, update, user_data, meet)

    order_data = {
        'options_provider': _ai_cafe_menu.options_provider(),
        'items_chosen': [],
        'meet': meet,
        'SN': 0
    }
    user_data[query.message.message_id] = order_data

    choose_options(bot, update, user_data)
    return "choose options"


@run_async
@choose_log
def choose_options(bot, update, user_data):
    query = update.callback_query
    order_data = user_data[query.message.message_id]

    if order_data['SN'] == 0:
        text, items = order_data['options_provider'].send(None)
    else:
        the_chosen, sn = query.data.split(', ')
        if str(order_data['SN']) == sn:
            order_data['items_chosen'].append(the_chosen)

            try:
                text, items = order_data['options_provider'].send(the_chosen)

            except StopIteration:
                order_data['order'] = _concat_chosen_items(order_data['items_chosen'])
                del order_data['options_provider'], order_data['items_chosen'], order_data['SN']

                return save_order(bot, update, user_data)

        else:
            query.answer(text='按慢點 廢物 (ゞω< )')
            return "choose options"

    order_data['SN'] += 1

    # TODO  auto resize the keyboard layout
    keyboard = [
        [InlineKeyboardButton(item, callback_data='{}, {}'.format(item, order_data['SN'])) for item in items],
        [InlineKeyboardButton("取消", callback_data="取消")]
    ]

    query.edit_message_text(text=text,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                            )

    return "choose options"


def save_order(bot, update, user_data):
    query = update.callback_query
    query_msg_id = query.message.message_id
    order_data = user_data[query_msg_id]
    meet = order_data['meet']
    order = order_data['order']

    if not meet.is_opening():
        cancel(bot, update, user_data)
        return ConversationHandler.END

    user = query.from_user
    data = {
        str(user.id): {'order': order,
                       'username': user.username,
                       'first_name': user.first_name,
                       'order_ids': (query.message.chat_id, query_msg_id),
                       'status': {'check_in': False,
                                  'paid': False,
                                  'got_drinks': False
                                  },
                       'cashier': None,
                       'timestamp': '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.today())
                       }
    }

    meet.update_order(data)
    meet.notify_observers(bot, with_button=True)

    del user_data[query_msg_id]

    return order_complete_page(query.message, meet, order)


@run_async
def cancel(bot, update, user_data, meet: Files.Meet = None):
    query = update.callback_query

    # If pass meet, it means that user_data was not initialized, also means user_data[query_msg_id] is not exist.
    if meet is None:
        query_msg_id = query.message.message_id
        meet = user_data[query_msg_id]['meet']
        del user_data[query_msg_id]

    data = meet.access_data()
    uid = str(query.from_user.id)
    if data is not None:

        if uid in data['order_users']:
            order = data['order_users'][uid]['order']

            if meet.is_opening():
                return order_complete_page(query.message, meet, order)

            query.answer(text=_meet_is_closed_notification, show_alert=True)
            return closed_page(query.message, meet, order)

        else:
            if meet.is_opening():
                return welcome_page(query.message, meet)

            query.answer(text=_meet_is_closed_notification, show_alert=True)
            query.edit_message_text(text=_did_not_order_text.format(meet=meet))

    else:
        query.answer(text=_record_is_not_exist_notification, show_alert=True)
        query.message.delete()

    return ConversationHandler.END


start_order = ConversationHandler(
    entry_points=[CallbackQueryHandler(init_order, pattern=r"^開始點餐, -?\d*, \d*$|^更改訂單, -?\d*, \d*$",
                                       pass_user_data=True)],
    states={
        "choose options": [CallbackQueryHandler(choose_options, pattern=r"^[^,]*, \d*$", pass_user_data=True),
                           CallbackQueryHandler(cancel, pattern=r"^取消$", pass_user_data=True)
                           ],
    },
    fallbacks=[],
    per_message=True
)

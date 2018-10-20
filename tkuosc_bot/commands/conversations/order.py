from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.error import BadRequest
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler

from tkuosc_bot.utils.decorators import log, choose_log, send_action
from tkuosc_bot.data_base import files

import re
import datetime
import base64


def _concat_chosen_items(items):
    # items means the list of item a user have chosen
    return '{} ({})'.format(*items[-2:])


def _add_order_and_update_participators_list(bot, meet, data):
    meet.add_order(data)

    text = '*participators:\n*' + '\n'.join('[{name}](tg://user?id={uid})  {order}'.format(
        uid=uid, name=data['username'] if data['username'] else data['first_name'], **data)
                                            for uid, data in meet.access_data()['order_users'].items())

    bot.edit_message_text(text=text,
                          chat_id=meet.chat_id,
                          message_id=meet.get_participators_msg_id(),
                          parse_mode='Markdown',
                          )


# TODO edit some config text
# _loading_text = random.choice(('這裡是 Loading 文字', '我是基德，是個 bot', '幫我想幹話'))  # 每週幹話，誰敢刪這行 ?

_loading_text = 'Loading...'
_welcome_page_text = '開放點餐囉~'
_stop_ordering_text = "結束惹 OwO\n我想放點 TOKEN 或 QRCode"
_ai_cafe_menu = files.Menu('Ai_cafe_drinks.json')


@log
@send_action(ChatAction.TYPING)
def start(bot, update, args, user_data):
    if args and re.match('^VkV0VlQxTkRlMEF4TlROck5ERj[A-Za-z0-9_-]{22}$', args[0]):
        special_bytes = base64.b64decode(args[0].translate(str.maketrans('-_', '+/')))

        meet_ids = (int.from_bytes(special_bytes[20:27], 'big', signed=True),
                    int.from_bytes(special_bytes[27:], 'big')
                    )
        meet = files.Meet(*meet_ids)

        if meet.is_open_meet():
            try:
                bot.get_chat_member(chat_id=meet_ids[0], user_id=update.message.from_user.id)
            except BadRequest:
                update.message.reply_text("歡迎使用 TKU-OSC Order 機器人，使用 /help 獲得更多資訊")
                return ConversationHandler.END

            return start_ordering(bot, update, user_data, meet)

    update.message.reply_text("歡迎使用 TKU-OSC Order 機器人，使用 /help 獲得更多資訊")

    return ConversationHandler.END


@log
def start_ordering(bot, update, user_data, meet):
    order_message = update.message.reply_text(text=_loading_text)
    order_ids = (order_message.chat_id, order_message.message_id)

    data = {
        order_ids[1]: {
            'meet': meet
        }
    }
    user_data.update(data)

    return welcome_page(bot, update, user_data, *order_ids)


def welcome_page(bot, update, user_data, order_chat_id, order_message_id):
    order_data = user_data[order_message_id]

    bot.edit_message_text(
        text='{}\n{}'.format(order_data['meet'].get_meet_name(), _welcome_page_text),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("開始點餐", callback_data="開始點餐")],
                                           ]),
        chat_id=order_chat_id,
        message_id=order_message_id
    )

    return "choose options"


@choose_log
def choose_options(bot, update, user_data):
    query = update.callback_query

    order_data = user_data[query.message.message_id]
    order_ids = (query.message.chat_id, query.message.message_id)

    if query.data in ("開始點餐", "更改訂單"):
        order_data.update(options_provider=_ai_cafe_menu.options_provider(),
                          items_chosen=[]
                          )

    elif query.data == "取消":
        del order_data['options_provider'], order_data['items_chosen']

        if 'order' in order_data:
            return order_complete_page(bot, update, user_data, *order_ids)
        else:
            return welcome_page(bot, update, user_data, *order_ids)

    order_data['items_chosen'].append(query.data)

    try:
        text, items = order_data['options_provider'].send(None if query.data in ("開始點餐", "更改訂單") else query.data)

    except StopIteration:
        order_data['order'] = _concat_chosen_items(order_data['items_chosen'])
        del order_data['options_provider'], order_data['items_chosen']

        return order_complete_page(bot, update, user_data, *order_ids)

    # TODO  auto resize the keyboard layout
    keyboard = [
        [InlineKeyboardButton(item, callback_data=item) for item in items],
        [InlineKeyboardButton("取消", callback_data="取消")]
    ]

    bot.edit_message_text(text=text,
                          reply_markup=InlineKeyboardMarkup(keyboard),
                          chat_id=order_ids[0],
                          message_id=order_ids[1]
                          )

    return "choose options"


def order_complete_page(bot, update, user_data, order_chat_id, order_message_id):
    order_data = user_data[order_message_id]

    bot.edit_message_text(
        text="{}\n訂單完成:\n{}".format(order_data['meet'].get_meet_name(), order_data['order']),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("更改訂單", callback_data="更改訂單")],
                                           ]
                                          ),
        chat_id=order_chat_id,
        message_id=order_message_id
    )

    # TODO  save order per user
    user = update.callback_query.from_user
    data = {
        str(user.id): {'order': order_data['order'],
                       'username': user.username,
                       'first_name': user.first_name,
                       'order_ids': (order_chat_id, order_message_id),
                       'show_up': False,
                       'paid': False,
                       'timestamp': '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.today()),
                       }
    }

    _add_order_and_update_participators_list(bot, order_data['meet'], data)

    return "order complete"


@log
def stop_ordering(bot, update, user_data):
    bot.edit_message_text(
        text='{}\n最後訂單: {}'.format(_stop_ordering_text,
                                   user_data.get('order', '你沒有填寫 QwQ')
                                   ),

        **user_data['order_message_ids']
    )

    # TODO  I wanna send some TOKEN or QRCode to final message
    # TODO  do something processing data

    user_data.clear()
    return ConversationHandler.END


order_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_args=True, pass_user_data=True)],
    states={
        "choose options": [CallbackQueryHandler(choose_options, pass_user_data=True)],
        "order complete": [CallbackQueryHandler(choose_options, pass_user_data=True)]
    },
    fallbacks=[CommandHandler('start', start, pass_args=True, pass_user_data=True)]
)

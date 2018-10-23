from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.error import BadRequest
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler

from tkuosc_bot.utils.decorators import log, choose_log, send_action
from tkuosc_bot.data_base import Files

import re
import datetime
import base64


def _concat_chosen_items(items):
    # items means the list of item a user have chosen
    return '{} ({})'.format(*items[-2:])


# TODO edit some config text
# _loading_text = random.choice(('這裡是 Loading 文字', '我是基德，是個 bot', '幫我想幹話'))  # 每週幹話，誰敢刪這行 ?

_loading_text = 'Loading...'
_welcome_page_text = '開放點餐囉~'
_ai_cafe_menu = Files.Menu('Ai_cafe_drinks.json')
_stop_ordering_text = "結束惹 OwO\n我想放點 TOKEN 或 QRCode"


@log
@send_action(ChatAction.TYPING)
def start(bot, update, args, user_data):
    if args and re.match('^VkV0VlQxTkRlMEF4TlROck5ERj[A-Za-z0-9_-]{22}$', args[0]):
        special_bytes = base64.b64decode(args[0].translate(str.maketrans('-_', '+/')))

        meet_ids = (int.from_bytes(special_bytes[20:27], 'big', signed=True),
                    int.from_bytes(special_bytes[27:], 'big')
                    )
        meet = Files.Meet(*meet_ids)

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

    for mid, data in user_data.items():
        if not meet.is_open_meet():
            del user_data[mid]

    data = {
        'meet': meet
    }
    user_data[order_message.message_id] = data

    return welcome_page(order_message, data)


def welcome_page(message, order_data):
    message.edit_text(text='{}\n{}'.format(order_data['meet'].name, _welcome_page_text),
                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("開始點餐", callback_data="開始點餐")]])
                      )

    return "choose options"


@choose_log
def choose_options(bot, update, user_data):
    query = update.callback_query

    order_data = user_data[query.message.message_id]

    if query.data in ("開始點餐", "更改訂單"):
        order_data['options_provider'] = _ai_cafe_menu.options_provider()
        order_data['items_chosen'] = []

    elif query.data == "取消":
        del order_data['options_provider'], order_data['items_chosen']

        if 'order' in order_data:
            return order_complete_page(bot, query.message, order_data)
        else:
            return welcome_page(query.message, order_data)

    order_data['items_chosen'].append(query.data)

    try:
        text, items = order_data['options_provider'].send(None if query.data in ("開始點餐", "更改訂單") else query.data)

    except StopIteration:
        order_data['order'] = _concat_chosen_items(order_data['items_chosen'])
        del order_data['options_provider'], order_data['items_chosen']

        return order_complete_page(bot, query, order_data)

    # TODO  auto resize the keyboard layout
    keyboard = [
        [InlineKeyboardButton(item, callback_data=item) for item in items],
        [InlineKeyboardButton("取消", callback_data="取消")]
    ]

    query.message.edit_text(text=text,
                            reply_markup=InlineKeyboardMarkup(keyboard)
                            )

    return "choose options"


def order_complete_page(bot, query, order_data):
    query.message.edit_text(text="{}\n訂單完成:\n{}".format(order_data['meet'].name, order_data['order']),
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("更改訂單", callback_data="更改訂單")]])
                            )

    # TODO  save order per user
    user = query.from_user
    data = {
        str(user.id): {'order': order_data['order'],
                       'username': user.username,
                       'first_name': user.first_name,
                       'order_ids': (query.message.chat_id, query.message.message_id),
                       'show_up': False,
                       'paid': False,
                       'timestamp': '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.today())
                       }
    }

    order_data['meet'].add_order(data)

    bot.edit_message_text(text=order_data['meet'].list_participators_with_markdown(),
                          chat_id=order_data['meet'].chat_id,
                          message_id=order_data['meet'].participators_msg_id,
                          parse_mode='Markdown',
                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('收單', callback_data='收單')]])
                          )

    return "order complete"


order_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_args=True, pass_user_data=True)],
    states={
        "choose options": [CallbackQueryHandler(choose_options, pass_user_data=True)],
        "order complete": [CallbackQueryHandler(choose_options, pass_user_data=True)]
    },
    fallbacks=[CommandHandler('start', start, pass_args=True, pass_user_data=True)]
)

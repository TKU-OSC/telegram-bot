from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import ConversationHandler
import json, random, datetime

from decorator import *


def options_provider():
    with open('drinks.json', 'r') as drinks_file:
        drinks_title, drinks_list = json.load(drinks_file)
        must_choose_title = drinks_title.pop()
        for title in drinks_title:
            chosen_one = yield title, tuple(drinks_list.keys())
            drinks_list = drinks_list[chosen_one]

        for must_choose_attribute in drinks_list.items():
            yield '{}: {}'.format(must_choose_title, must_choose_attribute[0]), tuple(must_choose_attribute[1])


def concat_chosen_items(items):
    # 這裡有個 List 是照順序按的東西 看你想怎樣輸出
    return '{}\n{}'.format(
        datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        ' -> '.join(item for item in items)
    )


# TODO edit some config text
# loading_text = random.choice(('這裡是 Loading 文字', '我是基德，是個 bot', '幫我想幹話'))  # 每週幹話，誰敢刪這行 ?

loading_text = 'Loading...'
welcome_page_text = '這週 xxx 開放點餐囉~ 之類的'
stop_ordering_text = "結束惹 OwO\n我想放點 TOKEN 或 QRCode"


@log
def start_ordering(bot, update, user_data):
    order_message = update.message.reply_text(text=loading_text)

    user_data['order_message_ids'] = dict(
        message_id=order_message.message_id,
        chat_id=order_message.chat_id
    )

    return welcome_page(bot, update, user_data)


def welcome_page(bot, update, user_data):
    bot.edit_message_text(
        text=welcome_page_text,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("開始點餐", callback_data="開始點餐")]
            ]
        ),
        **user_data['order_message_ids']
    )

    return "choose options"


@choose_log
def choose_options(bot, update, user_data):
    query = update.callback_query
    print(query.data)
    if query.data in ("開始點餐", "更改訂單"):
        user_data.update(dict(options_provider=options_provider(), items_chosen=[]))

    elif query.data == "取消":
        del user_data['options_provider'], user_data['items_chosen']

        if user_data.get('start_ordering', False):
            return order_complete(bot, update, user_data)
        else:
            return welcome_page(bot, update, user_data)

    user_data['items_chosen'].append(query.data)

    try:
        text, items = user_data['options_provider'].send(None if query.data in ("開始點餐", "更改訂單") else query.data)

    except StopIteration:
        user_data['start_ordering'] = concat_chosen_items(user_data['items_chosen'])
        del user_data['options_provider'], user_data['items_chosen']

        return order_complete(bot, update, user_data)

    # TODO  auto resize the keyboard layout
    keyboard = [
        [InlineKeyboardButton(item, callback_data=item) for item in items],
        [InlineKeyboardButton("取消", callback_data="取消")]
    ]

    bot.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        **user_data['order_message_ids']
    )

    return "choose options"


def order_complete(bot, update, user_data):
    bot.edit_message_text(
        text="訂單完成:\n{}".format(user_data['start_ordering']),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("更改訂單", callback_data="更改訂單")]
            ]
        ),
        **user_data['order_message_ids']
    )

    # TODO  save start_ordering per user

    return "start_ordering complete"


@log
def stop_ordering(bot, update, user_data):
    bot.edit_message_text(
        text='{}\n最後訂單: {}'.format(stop_ordering_text, user_data.get('start_ordering', '你沒有填寫 QwQ')),
        **user_data['order_message_ids']
    )

    # TODO  I wanna send some TOKEN or QRCode to final message
    # TODO  do something processing data

    user_data.clear()
    return ConversationHandler.END

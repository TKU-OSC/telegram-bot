import base64
import re

from telegram import ChatAction
from telegram.error import BadRequest
from telegram.ext import ConversationHandler, run_async

from tkuosc_bot.commands.conversations.order import start_ordering
from tkuosc_bot.data_base import Files
from tkuosc_bot.utils.decorators import log, send_action


@run_async
@log
@send_action(ChatAction.TYPING)
def start(bot, update, args):
    if args and re.match(r'^VkV0VlQxTkRlMEF4TlROck5ERj[A-Za-z0-9_-]{22}$', args[0]):
        special_bytes = base64.b64decode(args[0].translate(str.maketrans('-_', '+/')))

        meet_ids = (int.from_bytes(special_bytes[20:27], 'big', signed=True),
                    int.from_bytes(special_bytes[27:], 'big')
                    )
        meet = Files.Meet(*meet_ids)

        if meet.is_opening():
            try:
                bot.get_chat_member(chat_id=meet_ids[0], user_id=update.message.from_user.id)
            except BadRequest:
                update.message.reply_text("歡迎使用 TKU-OSC Order 機器人，使用 /help 獲得更多資訊")
                return

            return start_ordering(bot, update, meet)

    update.message.reply_text("歡迎使用 TKU-OSC Order 機器人，使用 /help 獲得更多資訊")



@run_async
@log
@send_action(ChatAction.TYPING)
def help_(bot, update):
    update.message.reply_text(''.join(line for line in
                                      '''
                                      /help
                                          show this
                                      /start
                                          pass args to join meet

                                      debug instruction:
                                      /getcid
                                          The chat_id of this group
                                      /getmid
                                          The message_id that you reply to
                                      '''.split(' ' * 38)
                                      )
                              )

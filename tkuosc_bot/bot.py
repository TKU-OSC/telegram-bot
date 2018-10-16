#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import ParseMode, ChatAction, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters
from tkuosc_bot.utils.conversation import *
from tkuosc_bot.utils.decorators import *


@log
@send_action(ChatAction.TYPING)
def start(bot, update):
    update.message.reply_text("歡迎使用 TKU-OSC Order 機器人，使用 /help 獲得更多資訊")


@log
@send_action(ChatAction.TYPING)
def help_(bot, update):
    update.message.reply_text(''.join(line for line in
                                      '''
                                      /help
                                         show this
                                      /start_ordering
                                          start a new meet up order
                                      /stop_ordering
                                          end the ordering
                                  
                                  
                                      debug instruction:
                                      /getme
                                          return your user_id
                                      /user_data
                                          return your user_data
                                      /chat_data
                                          return chat_data of this chat
                                      '''.split(' ' * 38)
                                      )
                              )


@log
@send_action(ChatAction.TYPING)
def getme(bot, update):
    if update.message.reply_to_message:
        reply_user = update.message.reply_to_message.from_user
        update.message.reply_text(text="`" + str(reply_user.id) + "`",
                                  quote=True,
                                  parse_mode=ParseMode.MARKDOWN
                                  )
    else:
        update.message.reply_text(text="`" + str(update.message.from_user.id) + "`",
                                  quote=True,
                                  parse_mode=ParseMode.MARKDOWN
                                  )


@log
@send_action(ChatAction.TYPING)
def user_data(bot, update, user_data):
    update.message.reply_text("`" + str(user_data) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@send_action(ChatAction.TYPING)
def chat_data(bot, update, chat_data):
    update.message.reply_text("`" + str(chat_data) + "`",
                              quote=True,
                              parse_mode=ParseMode.MARKDOWN
                              )


@log
@restricted
@send_action(ChatAction.TYPING)
def lsop(bot, update):
    with open(os.path.join(os.path.dirname(__file__), "../files/admin_list.txt"), 'r') as data:
        admins = {i.strip() for i in data}
        str_admin = '\n'.join(str(admin) for admin in sorted(admins))
        text = "管理員 UID：\n" + str_admin
        update.message.reply_text(text=text)


@log
@restricted
@send_action(ChatAction.TYPING)
def addop(bot, update, args):
    if not args:
        update.message.reply_text("請輸入 op 的 UID")
    else:
        with open(os.path.join(os.path.dirname(__file__), "../files/admin_list.txt"), 'r+') as data:
            admins = {i.strip() for i in data}
            for item in args:
                admins.add(item)
            data.seek(0)
            data.writelines("{}\n".format(i) for i in sorted(admins))
            data.truncate()
        update.message.reply_text("已新增新管理員")


@log
@restricted
@send_action(ChatAction.TYPING)
def deop(bot, update, args):
    if not args:
        update.message.reply_text("請輸入 op 的 UID")
    else:
        with open(os.path.join(os.path.dirname(__file__), "../files/admin_list.txt"), 'r+') as data:
            admins = {i.strip() for i in data}
            for item in args:
                if item == str(update.effective_user.id):
                    update.message.reply_text("你不應該移除自己，指令已中斷")
                    return
                if item not in admins:
                    update.message.reply_text("管理員不存在\n請查詢 /lsop 以獲得管理員清單")
                    return
                else:
                    admins.remove(item)
            data.seek(0)
            data.writelines("{}\n".format(i) for i in sorted(admins))
            data.truncate()
        update.message.reply_text("已移除管理員")


@log
@send_action(ChatAction.TYPING)
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Canceled',
                              reply_markup=ReplyKeyboardRemove())


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main(token):
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_))
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))

    # start_ordering the drinks
    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('start_ordering', start_ordering, pass_user_data=True)],
            states={
                "choose options": [CallbackQueryHandler(choose_options, pass_user_data=True)],
                "order complete": [CallbackQueryHandler(choose_options, pass_user_data=True)]
            },
            fallbacks=[CommandHandler('stop_ordering', stop_ordering, pass_user_data=True)]
        )
    )

    # debug instruction
    updater.dispatcher.add_handler(CommandHandler('getme', getme))
    updater.dispatcher.add_handler(CommandHandler('user_data', user_data, pass_user_data=True))
    updater.dispatcher.add_handler(CommandHandler('chat_data', chat_data, pass_chat_data=True))

    # Admin commands
    updater.dispatcher.add_handler(CommandHandler('lsop', lsop))
    updater.dispatcher.add_handler(CommandHandler('addop', addop, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('deop', deop, pass_args=True))

    # Error handler
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    TOKEN = os.environ.get('TOKEN', False) or input(
        'It seems like you don\'t have environment variable `TOKEN`.\nPlease enter it below:\n')
    # TODO  hide the input TOKEN
    main(TOKEN)

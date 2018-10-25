from telegram import ParseMode, ChatAction

from tkuosc_bot.data_base.Files import Admin
from tkuosc_bot.utils.decorators import log, restricted, send_action


@log
@restricted("TKUOSC.txt")
@send_action(ChatAction.TYPING)
def lsop(bot, update):
    admins = Admin("TKUOSC.txt").list()
    str_admin = ""
    for admin in sorted(admins):
        str_admin += "[{UID}](tg://user?id={UID})\n".format(UID=admin)
    text = "管理員 UID：\n" + str_admin
    update.message.reply_text(text=text,
                              parse_mode=ParseMode.MARKDOWN)


@log
@restricted("TKUOSC.txt")
@send_action(ChatAction.TYPING)
def addop(bot, update, args):
    if not args:
        update.message.reply_text("請輸入 op 的 UID")
    else:
        file = Admin("TKUOSC.txt")
        admins = file.list()
        for i in args:
            admins.add(i)
        file.write(admins)
        update.message.reply_text("已新增新管理員")


@log
@restricted("TKUOSC.txt")
@send_action(ChatAction.TYPING)
def deop(bot, update, args):
    if not args:
        update.message.reply_text("請輸入 op 的 UID")
    else:
        file = Admin("TKUOSC.txt")
        admins = file.list()
        for item in args:
            if item == str(update.effective_user.id):
                update.message.reply_text("你不應該移除自己，指令已中斷")
                return
            if item not in admins:
                update.message.reply_text("管理員不存在\n請查詢 /lsop 以獲得管理員清單")
                return
            else:
                admins.remove(item)
        file.write(admins)
        update.message.reply_text("已移除管理員")

import os

from telegram import ChatAction

from tkuosc_bot.utils.decorators import log, restricted, send_action


@log
@restricted
@send_action(ChatAction.TYPING)
def lsop(bot, update):
    with open(os.path.join(os.path.dirname(__file__), "../../files/TKUOSC.txt"), 'r') as data:
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
        with open(os.path.join(os.path.dirname(__file__), "../../files/TKUOSC.txt"), 'r+') as data:
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
        with open(os.path.join(os.path.dirname(__file__), "../../files/TKUOSC.txt"), 'r+') as data:
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

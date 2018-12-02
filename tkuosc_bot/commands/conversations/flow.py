from telegram import InlineKeyboardMarkup, InlineKeyboardButton, User
from telegram.ext import ConversationHandler, CallbackQueryHandler, run_async

from tkuosc_bot.data_base import Files
from tkuosc_bot.utils.concurrent_func import async_delete_msg
from tkuosc_bot.utils.decorators import choose_log


def _task(bot, update):
    query = update.callback_query
    meet_ids = query.data.split(', ')[1:]
    meet = Files.Meet(*meet_ids)
    user = query.from_user
    uid = str(user.id)
    orders = meet.access_data()['order_users']
    if uid in orders:
        status = orders[uid]['status']
        yield query, meet, uid, status, user

    else:
        query.answer(text="你並未參加 QwQ", show_alert=True, cache_time=86400)


@run_async
@choose_log
def check_in(bot, update):
    for query, meet, uid, status, user in _task(bot, update):
        if status['check_in']:
            query.answer(text="已經報到過ㄌ", cache_time=86400)
        else:
            meet.update_user_status(uid, 'check_in')
            query.answer(text="報到成功")
            meet.notify_observers(bot)


@run_async
@choose_log
def got_drinks(bot, update):
    for query, meet, uid, status, user in _task(bot, update):
        if status['check_in']:
            if status['paid']:
                if status['got_drinks']:
                    query.answer(text="已經拿到ㄌ", cache_time=86400)
                else:
                    meet.update_user_status(uid, 'got_drinks')
                    query.answer(text="享用愉快")
                    meet.notify_observers(bot)
            else:
                query.answer(text="請先結帳", show_alert=True)
        else:
            query.answer(text="請先報到", show_alert=True)


@run_async
@choose_log
def payment(bot, update, job_queue):
    for query, meet, uid, status, user in _task(bot, update):
        if status['check_in']:
            if status['paid']:
                query.answer(text="已經結帳過ㄌ", cache_time=86400)
            else:
                if len(job_queue.get_jobs_by_name(uid)) > 0:
                    query.answer(text='請耐心等待', show_alert=True, cache_time=5)
                    continue

                job = job_queue.run_once(payment_timeout, when=10, context=([], query.id), name=uid)
                text = user.mention_html() + ' 請求付款'
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton('確認款項', callback_data=f'結帳 {meet.chat_id} {meet.msg_id} {uid}')]])

                for admin in Files.Admin('TKUOSC.txt').list():
                    payment_confirm(bot, admin, text, keyboard, job)
        else:
            query.answer(text="請先報到", show_alert=True)


@run_async
def payment_confirm(bot, admin, text, keyboard, job):
    job.context[0].append(
        (admin, bot.send_message(text=text, chat_id=admin, reply_markup=keyboard, parse_mode='HTML').message_id)
    )


def payment_timeout(bot, job):
    for chat_id, msg_id in job.context[0]:
        async_delete_msg(bot, chat_id, msg_id)
    bot.answer_callback_query(job.context[1], text='無人回應 QwQ', show_alert=True)


@run_async
@choose_log
def checkout(bot, update, job_queue):
    query = update.callback_query
    args = query.data.split()[1:]
    meet = Files.Meet(*args[:-1])
    uid = args[-1]
    jobs = job_queue.get_jobs_by_name(uid)
    if len(jobs) != 1:
        query.answer(text='error', show_alert=True)
        return

    job = jobs[0]
    for meet_data in meet._update_meet():
        user_data = meet_data['order_users'][uid]
        user_status = user_data['status']
        if user_status['paid']:
            already_paid_alert(query, user_data)
        else:
            paid_success(bot, query, job.context)
            job.schedule_removal()
            user_status['paid'] = True
            user_data['cashier'] = query.from_user.id

    meet.notify_observers(bot)


@run_async
def already_paid_alert(query, user_data):
    query.answer(text=f"{user_data['cashier']} 收過錢ㄌ", show_alert=True)


@run_async
def paid_success(bot, query, context):
    query.answer(text="收款成功", show_alert=True)
    bot.answer_callback_query(context[1], text='付款成功', show_alert=True)
    for chat_id, msg_id in context[0]:
        async_delete_msg(bot, chat_id, msg_id)


check_in_handler = CallbackQueryHandler(check_in, pattern=r"^我到場了, -?\d*, \d*$")
got_drinks_handler = CallbackQueryHandler(got_drinks, pattern=r"^我拿到飲料了, -?\d*, \d*$")
payment_handler = CallbackQueryHandler(payment, pattern=r"^我要繳費, -?\d*, \d*$", pass_job_queue=True)
checkout_handler = CallbackQueryHandler(checkout, pattern=r"^結帳 -?\d* \d* \d*$", pass_job_queue=True)

import json
import os
from collections import Counter

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from tkuosc_bot.utils.concurrent_func import async_edit_msg


class Meet:
    _dir_path = os.path.join(os.path.dirname(__file__), '../../files/meet/')
    OPENING = "open"
    CLOSED = "close"
    NOT_EXIST = None

    def __init__(self, chat_id, message_id):
        self.chat_id = chat_id
        self.msg_id = message_id

        self.meet_id = '{}{}'.format(message_id, chat_id)
        self._name = None
        self._observers_msg = None

    @property
    def name(self):
        if self._name is None:
            self._name = self.access_data()['meet_name']
        return self._name

    @property
    def status(self):
        if self.is_opening():
            return self.__class__.OPENING
        elif self.is_closed():
            return self.__class__.CLOSED
        else:
            return self.__class__.NOT_EXIST

    @property
    def observers_msg(self):
        if self._observers_msg is None:
            self._observers_msg = self.access_data()['observers_msg']
        return self._observers_msg

    def open(self, meet_name):
        file_name = os.path.join(self.__class__._dir_path,
                                 'open/{}.json'.format(self.meet_id))
        with open(file_name, 'w') as meet_data:
            data = {
                'meet_name': meet_name,
                'observers_msg': [],
                'order_users': {}
            }
            json.dump(data, meet_data)

    def close(self):
        os.rename(os.path.join(self.__class__._dir_path, 'open/{}.json'.format(self.meet_id)),
                  os.path.join(self.__class__._dir_path, 'close/{}.json'.format(self.meet_id))
                  )

    def is_opening(self):
        """
        Check whether if the meet is open.
        :return: Boolean
        """
        dir_path = os.path.join(self.__class__._dir_path, 'open/')
        return '{}.json'.format(self.meet_id) in os.listdir(dir_path)

    def is_closed(self):
        dir_path = os.path.join(self.__class__._dir_path, 'close/')
        return '{}.json'.format(self.meet_id) in os.listdir(dir_path)

    def access_data(self):
        """
        Return the dictionary of the data of the meet.
        If the meet is not exist, then return None.
        :return: dictionary | None
        """
        if self.status is self.__class__.NOT_EXIST:
            return None

        file_name = os.path.join(self.__class__._dir_path, '{}/{}.json'.format(self.status, self.meet_id))
        with open(file_name, 'r') as data_file:
            return json.load(data_file)

    def has_user(self, uid):
        return str(uid) in self.access_data()['order_users']

    def _update_meet(self):
        file_name = os.path.join(self.__class__._dir_path, '{}/{}.json'.format(self.status, self.meet_id))
        with open(file_name, 'r+') as data_file:
            meet_data = json.load(data_file)
            yield meet_data

            data_file.seek(0)
            json.dump(meet_data, data_file)
            data_file.truncate()

    def update_order(self, order_data):
        for meet_data in self._update_meet():
            meet_data['order_users'].update(order_data)

    def add_observer_msg(self, msg):
        observer_msg = [msg.chat_id, msg.message_id]
        for meet_data in self._update_meet():
            if observer_msg not in meet_data['observers_msg']:
                meet_data['observers_msg'].append(observer_msg)
                self._observers_msg = meet_data['observers_msg']

    def update_user_status(self, uid, status):
        assert status in ('check_in', 'paid', 'got_drinks'), "Status is not exist"
        for meet_data in self._update_meet():
            meet_data['order_users'][uid]['status'][status] = True

    def list_participators_with_html(self):
        order_users = self.access_data()['order_users']
        if order_users:
            text = '<b>Participators:</b>\n' + '\n'.join(
                '<a href="tg://user?id={uid}">{name}</a>  {order}  {user_status}'.format(
                    uid=uid,
                    name=data['username'] if data['username'] else data['first_name'].replace('&', '&amp;').replace(
                        '<', '&lt;').replace('>', '&gt;'),
                    user_status=self.user_status_with_html(data), **data)
                for uid, data in order_users.items())
            return text

        return '<b>Participators:</b>\n' + '    Nobody now...'

    def list_items_with_html(self):
        items = Counter(user_data['order'] for user_data in self.access_data()['order_users'].values())
        text = '\n'.join(f"{item.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'): <20}"
                         f" {quantity:<3}" for item, quantity in items.most_common())
        return '<code>' + text + f'\n{f"總共有 {sum(items.values())} 筆": ^23}' '</code>'

    @staticmethod
    def user_status_with_html(data):
        status = data['status']
        if status['check_in']:
            if status['paid']:
                if status['got_drinks']:
                    text = '<code>飲料獲得</code>'
                else:
                    text = f'''<a href="tg://user?id={data['cashier']}">已結帳</a>'''
            else:
                text = '<code>到達</code>'
        else:
            text = ''
        return text

    def notify_observers(self, bot, with_button=False):
        text = self.list_participators_with_html()
        keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton('收單', callback_data='收單, {}, {}'.format(self.chat_id, self.msg_id))]]
                ) if with_button else None

        for chat_id, msg_id in self.observers_msg:
            async_edit_msg(bot, text, chat_id, msg_id, keyboard=keyboard, parse_mode="HTML")


class Menu:
    _dir_path = os.path.join(os.path.dirname(__file__), '../../files/menu/')

    def __init__(self, menu):
        """
        This menu file must fit the specified format
        :param menu: string
        """
        self.menu = menu

    def options_provider(self):
        """
        This options provider gives you a tuples of options.
        If you answer it with one of the options by `send` method,
            it will provide another tuples of options to you until raise a StopIteration.
        :return: generator
        """
        with open(os.path.join(self.__class__._dir_path, self.menu), 'r') as drinks_file:
            drinks_title, drinks_list = json.load(drinks_file)
            must_choose_title = drinks_title.pop()
            for title in drinks_title:
                chosen_one = yield title, tuple(drinks_list.keys())
                drinks_list = drinks_list[chosen_one]

            for must_choose_attribute in drinks_list.items():
                yield '{}: {}'.format(must_choose_title, must_choose_attribute[0]), tuple(must_choose_attribute[1])


class Admin:
    _dir_path = os.path.join(os.path.dirname(__file__), '../../files/admin/')

    def __init__(self, admin):
        self.admin = admin

    def add(self, uid):
        with open(os.path.join(self.__class__._dir_path, self.admin), 'a') as admin_file:
            admin_file.write(f'\n{uid}')

    def list(self):
        """
        :return: a list of admin
        """
        with open(os.path.join(self.__class__._dir_path, self.admin)) as admin_file:
            return [admin.strip() for admin in admin_file]

    def is_admin(self, uid):
        return str(uid) in self.list()

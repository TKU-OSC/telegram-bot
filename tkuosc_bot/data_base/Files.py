import os
import json


class Meet:
    _dir_path = os.path.join(os.path.dirname(__file__), '../../files/meet/')

    def __init__(self, chat_id, message_id):
        self.chat_id = chat_id
        self.msg_id = message_id

        self.meet_id = '{}{}'.format(message_id, chat_id)
        self._name = None
        self._participators_msg_id = None

    @property
    def name(self):
        if self._name is None:
            self._name = self.access_data()['meet_name']
        return self._name

    @property
    def participators_msg_id(self):
        if self._participators_msg_id is None:
            self._participators_msg_id = self.access_data()['participators_msg_id']
        return self._participators_msg_id

    def open(self, meet_name, participators_msg_id):
        file_name = os.path.join(self.__class__._dir_path,
                                 'open/{}.json'.format(self.meet_id))
        with open(file_name, 'w') as meet_data:
            data = {
                'meet_name': meet_name,
                'participators_msg_id': participators_msg_id,
                'order_users': {}
            }
            json.dump(data, meet_data)

    def close(self):
        os.rename(os.path.join(self.__class__._dir_path, 'open/{}.json'.format(self.meet_id)),
                  os.path.join(self.__class__._dir_path, 'close/{}.json'.format(self.meet_id))
                  )

    def is_open_meet(self):
        """
        Check whether if the meet is open.
        :return: Boolean
        """
        dir_path = os.path.join(self.__class__._dir_path, 'open/')
        return '{}.json'.format(self.meet_id) in os.listdir(dir_path)

    def access_data(self):
        """
        Return the dictionary of the data of the open meet.
        :return: dictionary
        """
        file_name = os.path.join(self.__class__._dir_path, 'open/{}.json'.format(self.meet_id))
        with open(file_name, 'r') as data_file:
            return json.load(data_file)

    def has_user(self, uid):
        return str(uid) in self.access_data()['order_users']

    def add_order(self, order_data):
        file_name = os.path.join(self.__class__._dir_path, 'open/{}.json'.format(self.meet_id))
        with open(file_name, 'r+') as data_file:
            meet_data = json.load(data_file)
            meet_data['order_users'].update(order_data)

            data_file.seek(0)
            json.dump(meet_data, data_file)
            data_file.truncate()

    def list_participators_with_markdown(self):
        order_users = self.access_data()['order_users']
        if order_users:
            text = '*Participators:*\n' + '\n'.join('[{name}](tg://user?id={uid})  {order}'.format(
                uid=uid, name=data['username'] if data['username'] else data['first_name'], **data)
                                                    for uid, data in order_users.items())
        else:
            text = '*Participators:*\n' + '    Nobody now...'
        return text


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

    def list(self):
        """
        :return: a list of admin
        """
        with open(os.path.join(self.__class__._dir_path, self.admin)) as admin_file:
            return [admin.strip() for admin in admin_file]

    def is_admin(self, uid):
        return str(uid) in self.list()

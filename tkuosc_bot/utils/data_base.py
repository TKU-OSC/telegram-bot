import os
import json


class Meet:
    _dir_path = os.path.join(os.path.dirname(__file__), '../../files/meet/')

    def __init__(self, chat_id, message_id):
        self.meet_id = '{}{}'.format(message_id, chat_id)
        self.name = None

    def initialize_meet(self, meet_name):
        file_name = os.path.join(Meet._dir_path,
                                 'open/{}.json'.format(self.meet_id))
        with open(file_name, 'w') as meet_data:
            data = {
                'meet_name': meet_name,
                'order_users': {}
            }
            json.dump(data, meet_data)

    def is_open_meet(self):
        """
        Check if the meet is open by pass its meet ids.
        :return: Boolean
        """
        dir_path = os.path.join(Meet._dir_path, 'open/')
        return '{}.json'.format(self.meet_id) in os.listdir(dir_path)

    def access_data(self):
        """
        Pass the meet ids, return the dictionary of meet data.
        :return: dictionary
        """
        file_name = os.path.join(Meet._dir_path, 'open/{}.json'.format(self.meet_id))
        with open(file_name, 'r') as data_file:
            return json.load(data_file)

    def get_meet_name(self):
        if self.name is None:
            self.name = self.access_data()['meet_name']
        return self.name

    def add_order(self, order_data):
        file_name = os.path.join(Meet._dir_path, 'open/{}.json'.format(self.meet_id))
        with open(file_name, 'r+') as data_file:
            meet_data = json.load(data_file)
            meet_data['order_users'].update(order_data)

            data_file.seek(0)
            json.dump(meet_data, data_file)
            data_file.truncate()


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
        with open(os.path.join(Menu._dir_path, self.menu), 'r') as drinks_file:
            drinks_title, drinks_list = json.load(drinks_file)
            must_choose_title = drinks_title.pop()
            for title in drinks_title:
                chosen_one = yield title, tuple(drinks_list.keys())
                drinks_list = drinks_list[chosen_one]

            for must_choose_attribute in drinks_list.items():
                yield '{}: {}'.format(must_choose_title, must_choose_attribute[0]), tuple(must_choose_attribute[1])


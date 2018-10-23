from setuptools import setup

with open('requirements.txt', 'r') as requirements:
    install_requires = [package for package in requirements]

setup(
    name='TKUOSC_OrderBot',
    version='0.1.isekai_dev0',
    packages=['tkuosc_bot',
              'tkuosc_bot.commands',
              'tkuosc_bot.commands.conversations',
              'tkuosc_bot.data_base',
              'tkuosc_bot.utils',
              ],
    install_requires=install_requires,
    python_requires='>=3',
    data_files=[('files/menu', ['files/menu/Ai_cafe_drinks.json']),
                ('files/meet/open/', ['files/meet/open/README']),
                ('files/meet/close', ['files/meet/close/README'])
                ],
    url='https://github.com/TKU-OSC/telegram-bot/tree/master',
    license='MIT',
    author='TKU-OSC Members',
    author_email='tkuosc@googlegroups.com',
    description='Just to deal with the order processs.'
)

from setuptools import setup

with open('requirements.txt', 'r') as requirements:
    install_requires = [package for package in requirements]

setup(
    name='TKUOSC_OrderBot',
    version='0.0.isekai_dev0',
    packages=['orderbot',
              'orderbot.utils'
              ],
    install_requires=install_requires,
    python_requires='>=3',
    data_files=[('datas', ['file/drinks.json'])],
    url='https://github.com/TKU-OSC/telegram-bot/tree/master',
    license='MIT',
    author='TKU-OSC Members',
    author_email='tkuosc@googlegroups.com',
    description='Just to deal with the order processs.'
)

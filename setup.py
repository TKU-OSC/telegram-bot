from setuptools import setup
import orderbot

with open('requirements.txt', 'r') as requirements:
    install_requires = [package for package in requirements]

setup(
    name='TKUOSC_OrderBot',
    version=orderbot.__version__,
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

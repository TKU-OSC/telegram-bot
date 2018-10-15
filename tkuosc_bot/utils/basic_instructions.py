from telegram import ChatAction
from tkuosc_bot.utils.decorators import log, send_action



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
                                      /create_meet_up
                                      /test
                                      '''.split(' ' * 38)
                                      )
                              )

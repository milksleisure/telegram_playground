#!/usr/bin/env python
from telegram.ext import Updater, CommandHandler

token = None
master = None

def hello(bot, update):
    user_id = update.message.from_user.id
    if user_id == int(master):
        message = 'Hello master!'
    else:
        message = 'Hello {}'.format(update.message.from_user.first_name)
    update.message.reply_text(message)

try:
    with open('mytoken') as ifd:
        token = ifd.read().rstrip()
    with open('masterid') as ifd:
        # Setup some functions that only specific users can use
        master = ifd.read().rstrip()
except:
    raise

updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.start_polling()
updater.idle()

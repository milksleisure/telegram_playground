#! /usr/bin/env python
import requests
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

META={
    'master': [],
    'token': None,
}

#Define the states
(COMMAND) = (0)

def parse_meta():
    try:
        with open('mytoken') as ifd:
            META['token'] = ifd.read().rstrip()
        with open('masterid') as ifd:
            # Setup some functions that only specific users can use
            META['master'].append(int(ifd.read().rstrip()))
    except:
        print('Meta insufficient info, refuse keep going')
        raise


def parse_command(cmd):
    result = cmd.split()
    return result

def get_ip():
    http_bin_address = 'https://httpbin.org/ip'
    r = requests.get(http_bin_address)
    return 'Your servant ip: {}'.format(r.json()['origin'])

PRIVATE_CMD={
    'ip': get_ip,
}
def do_priviledged_command(cmd):
    if len(cmd) < 1 or cmd[0] not in PRIVATE_CMD:
        return ('Invalid command sir! Available ones are: {}'
            .format(','.join(PRIVATE_CMD.keys())))
    function_name = cmd.pop(0)
    _f = PRIVATE_CMD[function_name]
    try:
        return _f(*cmd)
    except TypeError:
        return 'Error command usage sir!'

def do_normal_command(cmd):
    return None

def get_command_interface(update):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    user_command = update.message.text
    is_master = (user_id in META['master'])
    logger.info('user {}(id={},is_master={}) input command "{}"'.format(
        first_name, user_id, is_master, user_command))

    cmd = parse_command(user_command)
    if is_master:
        message = do_priviledged_command(cmd)
    else:
        message = do_normal_command(cmd)

    if message is not None:
        update.message.reply_text(message)


def start(bot, update):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    is_master = (user_id in META['master'])
    logger.info('user {}(id={},is_master={}) start the interface'.format(
        first_name, user_id, is_master))
    update.message.reply_text('Hello there! Please input something to start!')
    return COMMAND


def command(bot, update):
    get_command_interface(update)
    return COMMAND


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Ok, try to /start if more is required!')

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    parse_meta()

    updater = Updater(META['token'])
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            COMMAND: [MessageHandler(Filters.text, command)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

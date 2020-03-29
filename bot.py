from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

token = config['Telegram']['token']

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def get_image_url():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def list_public_chat():
    pass


def process_query():
    pass


def search(bot, update):  # search for a query
    chat_id = update.message.chat_id
    chat_text = update.message.text
    query = chat_text.split()[1:]
    query = ' '.join(query)
    bot.send_message(chat_id=chat_id, text=query)


def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text='Hello! I will help you to search in public channels. ')


def bop(bot, update):
    url = get_image_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


def main():
    pass
    # this is for bot activities
    # updater = Updater(token)
    # dp = updater.dispatcher
    # dp.add_handler(CommandHandler('bop', bop))
    # dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('search', search))
    # updater.start_polling()
    # updater.idle()


if __name__ == '__main__':
    main()

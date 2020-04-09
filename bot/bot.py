from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram import ParseMode, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction
import configparser
from telegram_info.search import Search

config = configparser.ConfigParser()
config.read("../telegram_info/config.ini")

token = config['Telegram']['token']


def search(bot, update):  # search for a query
    top_n = 2
    global searcher
    chat_id = update.message.chat_id
    chat_text = update.message.text
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    query = chat_text.split()[1:]
    query = ' '.join(query)
    # process query
    relevant_messages = searcher.search(query)
    bot.send_message(chat_id=chat_id, text=f'Search results for: *{query}*',
                     parse_mode=ParseMode.MARKDOWN)
    for msg in relevant_messages[:top_n]:
        bot.send_message(chat_id=chat_id, text=msg)

    menu_options = [[KeyboardButton('/c Show more')],
                    [KeyboardButton('/c Do not show')]]
    keyboard = ReplyKeyboardMarkup(menu_options)
    bot.send_message(chat_id=update.message.chat_id,
                     text='wow',
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=keyboard)


def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text='Hello! I will help you to search in public telegram channels. \n'
                                           'Send /search your query to search in channels. ')


def clear_search(bot, update):
    chat_id = update.message.chat_id
    menu_options = [[KeyboardButton('/c Show more')],
                    [KeyboardButton('/c Do not show')]]
    keyboard = ReplyKeyboardRemove(menu_options)
    bot.send_message(chat_id=update.message.chat_id,
                     text='wow',
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=keyboard)


def button_commands(bot, update):
    chat_id = update.message.chat_id
    chat_text = update.message.text
    command = chat_text.split()[1:]
    command = ' '.join(command)

    if command == 'Show more':
        pass
    elif command == 'Do not show':
        clear_search(bot, update)


def main():
    updater = Updater(token)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('search', search))
    dp.add_handler(CommandHandler('c', button_commands))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    searcher = Search(path_to_index='../telegram_info/index.pickle')
    main()

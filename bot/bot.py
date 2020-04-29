from telegram.ext import Updater, CommandHandler
from telegram import ParseMode, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, ChatAction
import configparser
import os
import logging
from search import Search

config = configparser.ConfigParser()
config.read("config.ini")
token = config['Telegram']['token']


class RufIndexer:
    def __init__(self):
        self.searcher = Search()
        self.search_results = {}
        self.menu_options = [[KeyboardButton('/c Show more')],
                             [KeyboardButton('/c Do not show')]]
        self.keyboard = ReplyKeyboardMarkup(self.menu_options)
        self.top_n = 3

        if not os.path.exists('../logs'):
            os.makedirs('../logs')

        self.logger = logging.getLogger("bot")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler("../logs/user_search.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    @staticmethod
    def sticker(bot, chat_id):
        with open('sticker.webp', 'rb') as f:
            return bot.send_sticker(chat_id, sticker=f, timeout=50).sticker

    def __search(self, bot, update):  # searcher for a query
        chat_id = update.message.chat_id
        chat_text = update.message.text
        bot.send_chat_action(chat_id=chat_id,
                             action=ChatAction.TYPING)  # indicate bot is doing something
        query = chat_text.split()[1:]
        query = ' '.join(query)
        relevant_messages = self.searcher.search(query)
        if not len(relevant_messages):
            bot.send_message(chat_id=chat_id,
                             text='Sorry, nothing was found for this query. ')
            bot.send_chat_action(chat_id=chat_id,
                                 action=ChatAction.TYPING)  # indicate bot is doing something
            self.sticker(bot, chat_id)
            return

        if len(relevant_messages[self.top_n:]):
            self.search_results[chat_id] = relevant_messages[self.top_n:]
        relevant_messages = relevant_messages[:self.top_n]

        bot.send_message(chat_id=chat_id,
                         text=f'Search results for: *{query}*',
                         parse_mode=ParseMode.MARKDOWN)
        for i, msg in enumerate(relevant_messages):
            bot.send_chat_action(chat_id=chat_id,
                                 action=ChatAction.TYPING)  # indicate bot is doing something
            if i == len(
                    relevant_messages) - 1 and chat_id in self.search_results:
                bot.send_message(chat_id=update.message.chat_id,
                                 text=msg,
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=self.keyboard)
            else:
                bot.send_message(chat_id=chat_id, text=msg)

    def __start(self, bot, update):
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id,
                         text='Hello! I will help you to searcher in public telegram channels. \n'
                              'Send /search your query to searcher in channels. ')

    def __clear_search(self, bot, update):
        chat_id = update.message.chat_id
        keyboard = ReplyKeyboardRemove(self.menu_options)
        bot.send_message(chat_id=chat_id,
                         text='That is it',
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=keyboard)
        self.search_results.pop(chat_id)

    def __show_more(self, bot, update):
        """
        Shows more searcher results than was shown to user previously
        :return:
        """
        chat_id = update.message.chat_id
        bot.send_chat_action(chat_id=chat_id,
                             action=ChatAction.TYPING)  # indicate bot is doing something
        relevant_messages = self.search_results[chat_id][:self.top_n]
        self.search_results[chat_id] = self.search_results[chat_id][
                                       self.top_n:]
        for i, msg in enumerate(relevant_messages):
            bot.send_chat_action(chat_id=chat_id,
                                 action=ChatAction.TYPING)  # indicate bot is doing something
            if i == len(relevant_messages) - 1 and len(
                    self.search_results[chat_id]):
                bot.send_message(chat_id=chat_id,
                                 text=msg,
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=self.keyboard)
            elif i == len(relevant_messages) - 1 and not len(
                    self.search_results[chat_id]):
                bot.send_message(chat_id=chat_id, text=msg)
                self.__clear_search(bot, update)
            else:
                bot.send_message(chat_id=chat_id, text=msg)

    def __button_commands(self, bot, update):
        chat_text = update.message.text
        command = chat_text.split()[1:]
        command = ' '.join(command)
        if command == 'Show more':
            self.__show_more(bot, update)
        elif command == 'Do not show':
            self.__clear_search(bot, update)

    def start_bot(self):
        updater = Updater(token)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler('start', self.__start))
        dp.add_handler(CommandHandler('search', self.__search))
        dp.add_handler(CommandHandler('c', self.__button_commands))
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    indexer_bot = RufIndexer()
    indexer_bot.start_bot()

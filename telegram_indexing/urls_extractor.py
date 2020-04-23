import nltk
import os
from pymongo import MongoClient
import logging
# from telegram_indexing.message_extractor import MessageExtractor
from preprocessing.message_parser import MessageParser

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')

"""
This file is capable for indexing
"""


class TelegramIndexer:
    def __init__(self):
        self.parser = MessageParser()
        self.visited_links = set()  # to keep track of links that we are going to visit during next iteration
        self.links_to_visit = set()  # to keep track of links that we are traveling through during current iteration
        self.index = {}
        self.doc_lengths = {}
        self.database_empty = True

        # create logger
        if not os.path.exists('../logs'):
            os.makedirs('../logs')
        self.logger = logging.getLogger("urls_extractor")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler("../logs/indexer.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        try:
            client = MongoClient()
            client = MongoClient("mongodb://127.0.0.1:27017/")
            self.logger.info('Connected to MongoDB successfully!!')
        except:
            self.logger.error('Could not connect to MongoDB')

        self.database = client.TelegramIndexerDB

    def index_one_url(self, url, messages):
        if url in self.visited_links:
            self.links_to_visit.discard(url)
            self.logger.info(f'Url {url} was already indexed. Move in to another url')
            return

        if not len(messages):
            self.links_to_visit.discard(url)
            self.logger.info(f'Message list is empty for url {url}')
            return

        self.logger.info(f'Indexing messages from url {url}')
        for msg_url, msg_text in messages.items():
            words, links = self.parser.parse_message(msg_text)
            self.links_to_visit.update(links)
            self.links_to_visit -= self.visited_links
            self.doc_lengths[msg_url] = len(words) # not precise but its okay
            # add words to index
            for w in words.keys():
                msg_freq = words[w]  # how many times occur in this particular message
                if w not in self.index:
                    self.index[w] = [msg_freq, (msg_url, msg_freq)]
                else:
                    self.index[w][0] += msg_freq
                    self.index[w].append((msg_url, msg_freq))
        self.visited_links.add(url)
        self.links_to_visit.discard(url)

    def dump_index(self):
        self.logger.info(f'Index is being dumped to DB')
        if self.database_empty:
            cursor = self.database.Index.find()
            i = 0
            for record in cursor:
                i += 1
                break
            if i > 0:
                self.database_empty = False

        if self.database_empty:
            self.logger.info(f'Database was empty, writing {len(self.index)} new items')
            for word, postings in self.index.items():
                try: self.database.Index.insert_one(
                    {'key': word, 'frequency': postings[0], 'postings': postings[1:]}
                )
                except:
                    self.logger.error(f'Unable to add new items to Index in database')

            for msg_url, doc_len in self.doc_lengths.items():
                try:
                    self.database.DocLengths.insert_one(
                        {'doc_url':msg_url, 'length': doc_len}
                    )
                except:
                    self.logger.error('Unable to add new items to DocLengths in database')
            self.index = {}  # local index is gonna be empty
            self.doc_lengths = {}
            return

        # Else, we have to merge new changes to existing index
        self.logger.info(f'Updating Index in database with new items')
        for word, postings in self.index.items():
            cursor = self.database.Index.find({'key': word})
            # 1. get existing index from db
            db_index = {}
            for record in cursor:
                db_index = record
            if not len(db_index):
                self.database.Index.insert_one(
                    {'key': word, 'frequency': postings[0], 'postings': postings[1:]}
                )
            else:
                self.logger.info(f'Changing existing postings')
                db_postings = db_index['postings']
                db_postings = {u: f for u, f in db_postings}
                for doc_url, doc_freq in postings[1:]:
                    db_postings[doc_url] = doc_freq
                db_postings = [[u, f] for u, f in db_postings.items()]
                frequency = 0
                for _, freq in db_postings:
                    frequency += freq
                myquery = {'key': word}
                newvalues = {"$set": {'frequency': frequency, 'postings': db_postings}}
                try:
                    self.database.Index.update_one(myquery, newvalues)
                    self.logger.info('Postings changed successfully')
                except:
                    self.logger.error('Postings were not changes, error while writing to database')

        self.logger.info('Updating DocLengths in the database')
        for doc_url, doc_len in self.index.items():
            cursor = self.database.Index.find({'doc_url': doc_url})
            # 1. get existing lengths from db
            db_index = {}
            for record in cursor:
                db_index = record
            if not len(db_index):
                self.database.DocLengths.insert_one(
                    {'doc_url': doc_url, 'length': doc_len}
                )
            else:
                self.logger.info(f'Changing doc lenths')
                myquery = {'doc_url': doc_url}
                newvalues = {"$set": {'length': doc_len}}
                try:
                    self.database.DocLengths.update_one(myquery, newvalues)
                    self.logger.info('DocLengths changed successfully')
                except:
                    self.logger.error('DocLengths were not changes, error while writing to database')

    # def index_first_time(self):  # ОТВЕЧАЕТ ЗА ИНДЕКСАЦИЮ ВСЕГО ПРОЦЕССА В ПЕРВЫЙ РАЗ
    #     base_url = 'https://t.me/Links'  # the public channel that we are going to start with
    #     self.links_to_visit.add(base_url)  # we are starting parsing from this url
    #     self.index_telegram_channels()
    #
    # def index_telegram_channels(self):
    #     msg_extract = MessageExtractor()
    #     while len(self.links_to_visit):
    #         for url in self.links_to_visit:
    #             messages = msg_extract.extract_all_messages(url)
    #             if not len(messages):
    #                 continue
    #             # print(messages)
    #             self.index_one_url(url, messages)
    #             self.dump_index()
    #             break
    #
    # def keep_index_updated(self):
    #     self.links_to_visit = self.visited_links
    #     self.visited_links = set()  # to keep track of links that we are going to visit during next iteration
    #     self.index_telegram_channels()

# if __name__ == '__main__':
#     indexer = TelegramIndexer()
#     indexer.index_first_time()
#     time.sleep(100)
#     indexer.keep_index_updated()

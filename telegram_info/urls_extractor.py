import nltk
from nltk.stem import WordNetLemmatizer
from collections import Counter
import pickle
import time
from telegram_info.message_extractor import MessageExtractor

nltk.download('wordnet')

"""
This file is capable for indexing
"""

class MessageParser:
    @staticmethod
    def lemmatize(word):
        lemmatizer = WordNetLemmatizer()
        return lemmatizer.lemmatize(word)

    def word_preprocess(self, word):
        words = nltk.word_tokenize(word)
        return [self.lemmatize(w.lower()) for w in words if w.isalpha()]

    def parse_message(self, msg):
        links = set()
        all_words = []
        for word in msg.split():
            if word.startswith('@'):
                # add it to links
                links.add(f'https://t.me/{word[1:]}')
            # process the word and add to index
            words = self.word_preprocess(word)
            all_words += words
        # print(links)
        return Counter(all_words), links


class TelegramIndexer:
    def __init__(self):
        self.parser = MessageParser()
        self.visited_links = set()  # to keep track of links that we are going to visit during next iteration
        self.links_to_visit = set()  # to keep track of links that we are traveling through during current iteration
        self.index = {}

    def index_one_url(self, url, messages):
        if url in self.visited_links:
            self.links_to_visit.discard(url)
            return
        for msg_url, msg_text in messages.items():
            # print(f'message url {msg_url}')
            words, links = self.parser.parse_message(msg_text)
            self.links_to_visit.update(links)
            self.links_to_visit -= self.visited_links
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

    def save_index(self):
        with open('index.pickle', 'wb') as f:
            pickle.dump(self.index, f)

    def index_telegram_channels(self):  # ОТВЕЧАЕТ ЗА ИНДЕКСАЦИЮ ВСЕГО ПРОЦЕССА
        base_url = 'https://t.me/Links'  # the public channel that we are going to start with
        msg_extract = MessageExtractor()
        messages = msg_extract.extract_all_messages(base_url)  # dictionary, for url contains all messages in that url
        self.links_to_visit.add(base_url)  # we are starting parsing from this url
        while len(self.links_to_visit):
            for url in self.links_to_visit:
                messages = msg_extract.extract_all_messages(url)
                if not len(messages):
                    continue
                self.index_one_url(url, messages)
                break
        # finished indexing, save it to disk
        self.save_index()

        # then sleep and run this indexing process again
        # time.sleep(10) # for a week
        # надо как то мониторить чтобы сообщения не посторяльсь, либо сделать dict в dict
        # print(self.index['language'])


if __name__ == '__main__':
    indexer = TelegramIndexer()
    indexer.index_telegram_channels()
    # with open('index.pickle', 'rb') as f:
    #     index = pickle.load(f)
    #
    # print(index['course'])

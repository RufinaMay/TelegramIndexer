import nltk
from nltk.stem import WordNetLemmatizer
from collections import Counter
from spellchecker import SpellChecker
from nltk.corpus import stopwords

nltk.download('wordnet')
nltk.download('stopwords')

class MessageParser:
    def __init__(self):
        self.spell_check = SpellChecker()
        self.stop_words = set(stopwords.words('english'))

    @staticmethod
    def lemmatize(word):
        lemmatizer = WordNetLemmatizer()
        return lemmatizer.lemmatize(word)

    def is_apt_word(self, word):
        return word not in self.stop_words # and word.isalpha()

    def word_preprocess(self, word):
        words = nltk.word_tokenize(word.lower())
        return [self.lemmatize(self.spell_check.correction(w)) for w in words if self.is_apt_word(w)]

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

import nltk

nltk.download("stopwords")
from nltk.corpus import stopwords
import spacy

"""
1. Analyze the task. We can make the following assumptions I guess:
- In telegram user are less likely to search for numbers or some formulas
- Most likely they arent gonna search for stop words
- Users can misspell stuff
- User might not know what word form was used in the original post
- Users might search for some close consept (which requires ML I suppose)

2. From these assumptions we can conclude that we need:
- lower text, remove stop words, lemmatize, remove non alphas
- add spellchecker 
"""


class Preprocessor:

    def __init__(self):
        self.russian_stopwords = stopwords.words('russian')
        self.english_stopwords = stopwords.words('english')
        self.ps = nltk.stem.PorterStemmer()

    # word tokenize text using nltk lib
    def tokenize(self, text):
        return nltk.word_tokenize(text)

    # stem word using provided stemmer
    # TODO: change it to lemmatization
    def stem(self, word, stemmer):
        return stemmer.stem(word)

    # check if word is appropriate - not a stop word and isalpha,
    # i.e consists of letters, not punctuation, numbers, dates
    def is_apt_word(self, word):
        return word not in self.english_stopwords and word not in self.russian_stopwords and word.isalpha()

    # combines all previous methods together
    # tokenizes lowercased text and stems it, ignoring not appropriate words
    def preprocess(self, text):
        tokenized = self.tokenize(text.lower())
        return [self.stem(w, self.ps) for w in tokenized if self.is_apt_word(w)]

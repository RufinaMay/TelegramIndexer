from pymongo import MongoClient
import math
import os
import logging
from collections import Counter
from message_parser import MessageParser


class Search:
    def __init__(self):
        self.parser = MessageParser()
        try:
            client = MongoClient("mongodb://127.0.0.1:27017/")
            print('Connected to MongoDB successfully!!')
        except:
            print('Could not connect to MongoDB')

        self.database = client.TelegramIndexerDB # client.TelegramMusicIndexerDB

        # define separate logger for searcher and bot logger
        if not os.path.exists('../../logs'):
            os.makedirs('../../logs')

        self.logger = logging.getLogger("searcher")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler("../../logs/user_search.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)


    def search(self, query):
        query_terms, links = self.parser.parse_message(query)
        # now organize the searcher in the index
        # relevant_documents = self.boolean_retrieval(query_terms)
        relevant_documents = self.okapi_scoring(query_terms)
        return relevant_documents

    def boolean_retrieval(self, query):
        # 1. first get data from index in database
        postings = []
        for term in query.keys():
            posting = []
            cursor = self.database.Index.find({'key': term})
            for record in cursor:
                posting += record['postings']

            # extract document info only
            posting = [i[0] for i in posting]
            postings.append(posting)
        if not len(postings):
            return []
        docs = list(set.intersection(*map(set, postings)))
        return docs

    def okapi_scoring(self, query, k1=1.2, b=0.75):
        scores = Counter()
        N = self.database.Index.count()
        avgdl = 100 # constant for all documents, not gonna calculate
        for term in query.keys():
            # extract postings lists from Index
            postings = []
            cursor = self.database.Index.find({'key': term})
            for record in cursor:
                postings += record['postings']
            if not len(postings):
                continue  # ignore absent terms

            # if term is present in the database, then we calculate okapi
            # score for each document
            n_docs = len(postings) - 1
            idf = math.log10((N - n_docs + 0.5) / (n_docs + 0.5))
            for posting in postings:
                doc_id = posting[0]
                doc_tf = posting[1]
                doc_len = 0
                cursor = self.database.DocLengths.find({'doc_url':doc_id})
                for record in cursor:
                    doc_len = record['length']
                if not doc_len:
                    doc_len = 0
                score = idf * doc_tf * (k1 + 1) / (doc_tf + k1 * (
                            1 - b + b * (doc_len / avgdl)))
                scores[doc_id] += score

        # sort according to the score value
        scores = scores.most_common()
        documents = [doc_url for doc_url, _ in scores]

        return documents


if __name__ == '__main__':
    searcher = Search()
    print(searcher.search('language'))

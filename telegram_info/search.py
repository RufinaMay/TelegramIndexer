from pymongo import MongoClient
from preprocessing.message_parser import MessageParser


class Search:
    def __init__(self):
        self.parser = MessageParser()
        try:
            client = MongoClient()
            client = MongoClient("mongodb://localhost:27017/")
            print('Connected to MongoDB successfully!!')
        except:
            print('Could not connect to MongoDB')

        self.database = client.TelegramIndexerDB

    def search(self, query):
        query_terms, links = self.parser.parse_message(query)
        # now organize the search in the index
        relevant_documents = self.boolean_retrieval(query_terms)
        return relevant_documents

    def boolean_retrieval(self, query):
        # 1. first get data from index in database
        postings = []
        posting = []
        for term in query.keys():
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


if __name__ == '__main__':
    searcher = Search()
    print(searcher.search('language'))

import json
import logging
from pprint import pprint
from time import sleep

import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

def connect_elasticsearch():
    """Connect to elastic search server"""
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connected')
    else:
        print('Awww it could not connect!')
    return _es


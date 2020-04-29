FROM python:3

ADD config.ini /
ADD RufIndexer.session /
ADD urls_extractor.py /
ADD messages_indexer.py /
ADD preprocessing/message_parser.py /

ADD requirements /
RUN pip3 install --no-cache-dir -r requirements

WORKDIR /

CMD [ "python3", "messages_indexer.py" ]
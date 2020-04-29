FROM python:3

ADD /preprocessing/message_parser.py /
ADD /searcher/search.py /
ADD bot.py /
ADD sticker.webp /
ADD config.ini /

ADD requirements /
RUN pip3 install --no-cache-dir -r requirements

WORKDIR /

CMD [ "python3", "bot.py" ]

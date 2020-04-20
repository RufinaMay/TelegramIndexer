FROM python:3
ADD ../telegram_info/message_extractor.py /

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./telegram_info/message_extractor.py" ]
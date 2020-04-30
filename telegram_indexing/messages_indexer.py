from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import configparser
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import time
import logging
import os
from urls_extractor import TelegramIndexer


# TODO: in this file add exception handler

class MessageExtractor:
    def __init__(self):
        # Reading Configs
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Setting configuration values
        api_id = config['Telegram']['api_id']
        api_hash = config['Telegram']['api_hash']
        api_hash = str(api_hash)
        self.phone = config['Telegram']['phone']
        username = config['Telegram']['username']

        # Create the client and connect
        self.client = TelegramClient(username, api_id, api_hash)

        # define some constants to limit the messages read
        self.limit = 100  # maximum messages that we can read during one session
        self.total_count_limit = 1000  # how many messages in total we will consider from each chat

        # define the indexer that will process all messages and them into index
        self.indexer = TelegramIndexer()

        # define logger
        if not os.path.exists('../logs'):
            os.makedirs('../logs')

        self.logger = logging.getLogger("message_extractor")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler("../logs/indexer.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.info("Message extractor started")

    async def get_channel_data(self, channel_url):
        """
        :param channel_url:
        :return:
        """
        await self.client.start()
        self.logger.info(f'Client Created for url {channel_url}')

        # Ensure you're authorized
        if await self.client.is_user_authorized() == False:
            await self.client.send_code_request(self.phone)
            try:
                await self.client.sign_in(self.phone,
                                          input('Enter the code: '))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input('Password: '))

        self.logger.info(f'Authorization complete for url {channel_url}')

        me = await self.client.get_me()
        my_channel = await self.client.get_entity(channel_url)
        offset_id = 0
        total_messages = 0

        self.logger.info(f'Starting indexing url {channel_url}')

        while True:
            history = await self.client(GetHistoryRequest(
                peer=my_channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=self.limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                self.logger.info(
                    f'No more messages found for url {channel_url}')
                break

            messages = history.messages
            all_messages = {}
            for message in messages:
                message_dict = message.to_dict()
                message_content = ''
                media_mime_type = ''
                audio_title = ''
                audio_performer = ''
                try:
                    message_content = message_dict['message']
                    message_media = message_dict['media']['document']
                    media_mime_type = message_media['mime_type']
                except KeyError:
                    pass
                # we will index this item if it is a song
                if 'audio' in media_mime_type:
                    print(f'audio file detected')
                    try:
                        message_media_attributes = message_media['attributes']
                        audio_title = message_media_attributes['title']
                        audio_performer = message_media_attributes['performer']
                    except KeyError:
                        pass
                    # add new songs to all messages
                    message_id = message_dict['id']
                    all_messages[
                        f'{channel_url}/{message_id}'] = message_content + audio_title + audio_performer

            if not len(all_messages):
                self.logger.info(
                    f'No more messages found for url {channel_url}')
                break
            else:
                self.logger.info(
                    f'{len(all_messages)} messages were found for url {channel_url}')

            self.logger.info(
                f'{len(all_messages)} messages found for url {channel_url}')
            offset_id = messages[len(messages) - 1].id
            total_messages += len(all_messages)
            self.indexer.index_one_url(channel_url,
                                       all_messages)  # index messages that we just read

            if self.total_count_limit != 0 and total_messages >= self.total_count_limit:
                self.logger.info(
                    f'Total number of messages ({self.total_count_limit}) reached, stop parsing url {channel_url}')
                break

        return all_messages

    def extract_all_messages(self, url):
        """
        :param url: list of telegram channel urls
        :return:
        """
        with self.client:
            try:
                messages = self.client.loop.run_until_complete(
                    self.get_channel_data(url))
            except:
                messages = []
        return messages

    def index_first_time(
            self):  # ОТВЕЧАЕТ ЗА ИНДЕКСАЦИЮ ВСЕГО ПРОЦЕССА В ПЕРВЫЙ РАЗ
        self.indexer.links_to_visit = {'https://t.me/muzikys',
                                       'https://t.me/Links',
                                       'https://t.me/music_muzyka'}  # the public channel that we are going to start with
        self.index_telegram_channels()

    def keep_index_updated(self):
        self.logger.info('Indexer is turning to uodate mode')
        self.indexer.links_to_visit = self.indexer.visited_links
        self.indexer.visited_links = set()  # to keep track of links that we are going to visit during next iteration
        self.index_telegram_channels()

    def index_telegram_channels(self):
        while len(self.indexer.links_to_visit):
            for url in self.indexer.links_to_visit:
                self.extract_all_messages(url)
                self.indexer.dump_index()  # dump index happens every time we finish indexing one channel
                break
            if len(self.indexer.visited_links) > 1000:
                break


if __name__ == '__main__':
    msg_extract = MessageExtractor()
    msg_extract.index_first_time()
    msg_extract.logger.info(
        'Indexer is turning to keep track on changes since now')
    print('Indexer is turning to keep track on changes since now')
    # while True:
    #     time.sleep(86400)
    #     msg_extract.keep_index_updated()

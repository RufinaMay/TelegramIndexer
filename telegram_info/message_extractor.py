from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import configparser
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel


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
        self.total_count_limit = 300  # how many messages in total we will consider from each chat

    async def authorize(self):
        if await self.client.is_user_authorized() == False:
            await self.client.send_code_request(self.phone)
            try:
                await self.client.sign_in(self.phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input('Password: '))

    async def get_channel_data(self, chanel_url):
        """

        :param chanel_url:
        :return:
        """
        await self.client.start()
        print("Client Created")

        # Ensure you're authorized
        self.authorize()

        me = await self.client.get_me()
        my_channel = await self.client.get_entity(chanel_url)
        all_messages = {}
        offset_id = 0

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
                break
            messages = history.messages
            for message in messages:
                # print(message.to_dict())
                message_dict = message.to_dict()
                # print(message_dict)
                # print('============================================================================')
                message_content = ''
                try:
                    message_content = message_dict['message']
                except KeyError:
                    pass
                message_id = message_dict['id']
                all_messages[f'{chanel_url}/{message_id}'] = message_content
            offset_id = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if self.total_count_limit != 0 and total_messages >= self.total_count_limit:
                break

        return all_messages

    def extract_all_messages(self, url):
        """

        :param urls: list of telegram channel urls
        :return:
        """
        with self.client:
            try: messages = self.client.loop.run_until_complete(self.get_channel_data(url))
            except: messages = ''
        return messages


if __name__ == '__main__':
    msg_extract = MessageExtractor()
    url_message = msg_extract.extract_all_messages('https://t.me/Links')
    print(url_message)

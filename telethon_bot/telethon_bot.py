import logging
from telethon import TelegramClient, events
import re
import requests
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

channels = CHANNEL_IDS.split(' ')

def convert_to_int_or_leave_as_string(element):
    try:
        return int(element)
    except ValueError:
        return element

channel_ids = [convert_to_int_or_leave_as_string(element) for element in channels]

client = TelegramClient(SESSION_STR, API_ID, API_HASH)

print(channel_ids)

registered_coins = []

def get_coin(msg):
    return re.findall('[1-9A-HJ-NP-Za-km-z]{32,44}', msg)

@client.on(events.NewMessage(chats=channel_ids))
async def channel_message_handler(event):
    print(f"Message in chat {event.chat_id}: {event.raw_text}")
    matches = get_coin(event.raw_text)
    if(len(matches) > 0):
        coin = matches[0]
        if(coin not in registered_coins):
            registered_coins.append(coin)
            requests.get(f'http://localhost:3000/buy/{coin}')
        print(f'List of coins {registered_coins}')

async def main():
    logger.info("Starting the client")
    await client.start()
    me = await client.get_me()
    logger.info(f"Logged in as: {me.username}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
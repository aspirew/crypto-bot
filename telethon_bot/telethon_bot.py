from telethon_service import *
import asyncio
from monitoring_service import monitor_coins_price

async def price_monitoring():
    while True:
        await monitor_coins_price()
 
async def main():
    logger.info("Starting the client")
    await client.start()
    me = await client.get_me()
    logger.info(f"Logged in as: {me.username}")
    # client.loop.create_task(price_monitoring())
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())

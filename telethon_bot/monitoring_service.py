from coin_service import get_all_active
import asyncio
from telethon_service import save_or_check_coin

async def monitor_coins_price():
    all_coins = get_all_active()
    for coin in all_coins:
        if(coin['growth'] > -0.8):
            print(f"Checking price of {coin['name']}")
            await save_or_check_coin(coin['hash_id'])
        else:
            print(f"Skipping {coin['name']}...")
    await asyncio.sleep(600)
    

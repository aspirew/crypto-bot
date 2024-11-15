from telethon import TelegramClient, events
from config import *
import re
from coin_service import update_growth, sell_coin, buy_coin, get_coin, get_all_active_coins, buy_or_update_coin, get_coin_data_from_bot, calculate_growth, get_users_statistics, clearup_invalid_coins, should_buy
import emoji
import asyncio
from dex_screener_service import get_coin_info

def convert_to_int_or_leave_as_string(element):
    try:
        return int(element)
    except ValueError:
        return element

channels = CHANNEL_IDS.split(' ')

channel_ids = [convert_to_int_or_leave_as_string(element) for element in channels]
admin_id = convert_to_int_or_leave_as_string(ADMIN_ID)
bot_id = convert_to_int_or_leave_as_string(BOT_ID)

client = TelegramClient(SESSION_STR, API_ID, API_HASH)

channel_id = 0
sender_id = None
buy_g = False
expected_sell_time_in_minutes_g = 0
expected_growth_g = 0

def get_coin_regex(msg):
    return re.findall('[1-9A-HJ-NP-Za-km-z]{32,44}', msg)

async def save_or_check_coin(coin, buy = False, expected_sell_time_in_minutes = 0, expected_growth = 0):
    dex_screener_response = await get_coin_info([coin])
    if(dex_screener_response is not None):
        base_token = dex_screener_response['baseToken']
        name = base_token['name']
        price = dex_screener_response['priceNative']
        buy_or_update_coin(name, coin, price, channel_id, sender_id, buy, expected_sell_time_in_minutes, expected_growth)
    else:
        print("Trying old method instead...")
        buy_g = buy
        expected_sell_time_in_minutes_g = expected_sell_time_in_minutes
        expected_growth_g = expected_growth
        await asyncio.sleep(1)
        await client.send_message(BOT_ID, coin)

@client.on(events.NewMessage(chats=channel_ids))
async def channel_message_handler(event):
    matches = get_coin_regex(event.raw_text)
    global channel_id, sender_id
    try:
        sender = await client.get_entity(event.message.sender_id)  
        sender_id = sender.username or str(event.message.sender_id)
    except ValueError:
        sender_id = str(event.message.sender_id)
    if(len(matches) > 0 and "bot" not in sender_id.lower()):
        channel_id = event.chat.title if event.chat else event.chat_id
        print("New call on channel ", channel_id, " from ", sender_id)
        determine_call = should_buy(sender_id)
        if(determine_call['buy'] is False):
            print("Untrusted caller, just obeserving new call...")
            await save_or_check_coin(matches[0], False)
        else:
            print("Trusted caller! Buying a coin...")
            msg = "💲 Found new trusted call!\n" + ":technologist: Caller: " + sender_id + "\n:dollar_banknote: Expected return: " + str(determine_call['expected_growth']) + "\n:hourglass_not_done: Average return time: " + str(determine_call['expected_sell_time_in_minutes']) + " minutes"
            await client.send_message(admin_id, emoji.emojize(msg))
            await save_or_check_coin(matches[0], True, determine_call['expected_sell_time_in_minutes'], determine_call['expected_growth'])

@client.on(events.NewMessage(chats=admin_id))
async def admin_message_handler(event):
    text = event.raw_text
    if("/coins" in text):
        coins = get_all_active_coins()
        for coin in coins:
            await asyncio.sleep(2)
            name = "💲 " + coin['name'] + ' - ' + coin['hash_id'] + "\n"
            growth_emoji = ":red_square:" if coin['growth'] < 0 else ":green_square:"
            growth = emoji.emojize(growth_emoji, language='alias')  + " Growth: " + str(coin['growth'] * 100) + '%' + "\n"
            highest = ":chart_increasing:"
            if(coin['buying_price'] == coin['highest_price']):
                highest += " The coin never exceeded call value :melting_face: \n"
            else:
                max_growth = calculate_growth(float(coin['buying_price']), float(coin['highest_price'])) * 100
                highest += str(coin['highest_price']) + " $ => " + str(max_growth) + " %\n" 
            highest = emoji.emojize(highest)
            lowest = ":chart_decreasing:"
            if(coin['buying_price'] == coin['lowest_price']):
                lowest += " The coin never went below call value :start_struck: \n"
            else:
                min_growth = calculate_growth(float(coin['buying_price']), float(coin['lowest_price'])) * 100
                lowest += str(coin['lowest_price']) + " $ => " + str(min_growth) + " %\n" 
            lowest = emoji.emojize(lowest)
            call_info = "Called on " + str(coin['channel_id']) + " by " + str(coin['user_id']) + "\n"
            await client.send_message(admin_id, name + growth + highest + lowest + call_info)
    elif("/stats" in text):
        users = get_users_statistics()
        print(users)
        for user_data in users:
            # Unpack all the metrics
            coin_with_growth = user_data['coin_with_growth']
            trust = user_data['trust']
            avg_growth = user_data['average_growth']
            median_growth = user_data['median_growth']
            stddev_growth = user_data['stddev_growth']
            avg_drawdown = user_data['average_drawdown']
            avg_peak_timing = user_data['average_peak_timing']
            short_term_win_rate = user_data['short_term_win_rate']
            medium_term_win_rate = user_data['medium_term_win_rate']
            long_term_win_rate = user_data['long_term_win_rate']
            user = user_data['user']
            
            # User information and trust level
            user_str = str(user) + '\n'
            trust_str = ":red_square: " if trust < 0.3 else ":green_square: " if trust > 0.7 else ":yellow_square: "
            trust_str += " Trust: " + f"{trust * 100:.1f} %\n\n"
            
            # General stats about growth and drawdown
            stats_str = (
                f"Average Growth: {avg_growth * 100:.2f} %\n"
                f"Median Growth: {median_growth * 100:.2f} %\n"
                f"Growth Volatility (Std Dev): {stddev_growth * 100:.2f} %\n"
                f"Average Drawdown: {avg_drawdown * 100:.2f} %\n"
                f"Average Peak Timing: {avg_peak_timing:.1f} minutes\n\n"
            )
            
            # Short, medium, and long-term win rates
            win_rates_str = (
                f"Short-Term Win Rate (<=1 hour): " + (":green_square: " if short_term_win_rate > 0.7 else ":yellow_square: " if short_term_win_rate > 0.3 else ":red_square: ")
                + f"{short_term_win_rate * 100:.1f} %\n"
                f"Medium-Term Win Rate (1 hour - 12 hours): " + (":green_square: " if medium_term_win_rate > 0.7 else ":yellow_square: " if medium_term_win_rate > 0.3 else ":red_square: ")
                + f"{medium_term_win_rate * 100:.1f} %\n"
                f"Long-Term Win Rate (>12 hours): " + (":green_square: " if long_term_win_rate > 0.7 else ":yellow_square: " if long_term_win_rate > 0.3 else ":red_square: ")
                + f"{long_term_win_rate * 100:.1f} %\n\n"
            )

            # Detailed coin calls
            all_calls_str = ""
            for coin_with_g in coin_with_growth:
                growth = coin_with_g['growth'] * 100
                c_name = coin_with_g['name']
                square = ":red_square: " if growth < 20 else ":green_square: " if growth > 100 else ":yellow_square: "
                all_calls_str += f"{square}{c_name} : {growth:.2f} %\n"
            
            # Send the composed message
            message = emoji.emojize(user_str + trust_str + stats_str + win_rates_str + all_calls_str)
            await client.send_message(admin_id, message)
    elif("/clear" in text):
        coins_deleted = clearup_invalid_coins()
        await client.send_message(admin_id, f"Coins deleted: {coins_deleted}")

@client.on(events.MessageEdited(chats=bot_id))
async def bot_edit_event_handler(event):
    text = event.raw_text
    if("⇄" in text):
        buy_or_update_coin(*get_coin_data_from_bot(text), channel_id, sender_id, buy_g, expected_sell_time_in_minutes_g, expected_growth_g)


from db import save_entry, get_entry, update_entry, get_all_active, Status, remove_entry, get_all
import re
from datetime import datetime
from statistics import mean, median, stdev

def buy_coin(name, hashId, price, channel_id, sender_id, expected_sell_time_in_minutes, expected_growth):
    save_entry(name, hashId, price, channel_id, sender_id, expected_sell_time_in_minutes, expected_growth)

def sell_coin(name):
    update_entry(name, { 'status': Status.sold.value })

def calculate_growth(buying_price, highest_price):
    return round((highest_price - buying_price) / buying_price, 2) if buying_price > 0 else 0

def calculate_drawdown(buying_price, lowest_price):
    return round((lowest_price - buying_price) / buying_price, 2) if buying_price > 0 else 0

def update_growth(name, current_price):
    coin = get_entry(name)
    new_price = float(current_price)
    old_price = float(coin['highest_price'])
    growth = calculate_growth(old_price, new_price)
    if(new_price > old_price):
        update_entry(name, { 'highest_price': current_price, 'highest_on': str(datetime.now()) })
    if(new_price < old_price):
        update_entry(name, { 'lowest_price': current_price, 'lowest_on': str(datetime.now()) })
    update_entry(name, { 'growth': growth })

def get_coin(name):
    return get_entry(name)

def get_all_active_coins():
    return get_all_active()

def buy_or_update_coin(name, hashId, price, channel_id, sender_id, buy, expected_sell_time_in_minutes, expected_growth):
    coin = get_coin(name)
    if(coin is not None):
        update_growth(name, price)
    else:
        print("Buying a new coin ", name, " from ", channel_id)
        buy_coin(name, hashId, price, channel_id, sender_id, expected_sell_time_in_minutes, expected_growth)
        if(buy is True):
            # try to buy the coin through telegram bot and then update status
            update_entry(name, { 'status': Status.BOUGHT.value })

def get_coin_data_from_bot(message):
    normalized_price = 0
    token_name = ''
    token_hash = ''

    price_pattern = r"Price:\s*\$(\d+(?:\.\d+)?(?:\(\d+\))?\d*)"
    match_price = re.search(price_pattern, message)
    if match_price:
        raw_price = match_price.group(1)
        normalized_price = re.sub(r"\((\d+)\)", lambda m: '0' * int(m.group(1)), raw_price)

    token_name_pattern = r"Buy\s+\$(\w+)"
    match_token_name = re.search(token_name_pattern, message)
    if match_token_name:
        token_name = match_token_name.group(1)

    token_hash = re.findall('[1-9A-HJ-NP-Za-km-z]{32,44}', message)[0]

    return token_name, token_hash, normalized_price

def get_users_statistics():
    coins = get_all_active_coins()
    all_users = set(map(lambda x: x['user_id'], coins))
    users = []
    for user in all_users:
        users.append(get_user_statistics(coins, user))
    return sorted(users, key=lambda entry: entry['trust'], reverse=True)

def get_user_statistics(user): 
    coins = get_all_active_coins()

    # Filter coins called by the specified user
    coins_of_user = list(filter(lambda x: str(x['user_id']) == str(user), coins)) 

    # Growth and drawdown for each coin
    coin_stats = []
    for c in coins_of_user:
        growth = calculate_growth(float(c['buying_price']), float(c['highest_price']))
        drawdown = calculate_drawdown(float(c['buying_price']), float(c['lowest_price']))
        holding_time = datetime.fromisoformat(c['highest_on']) - datetime.fromisoformat(c['created_on'])
        peak_timing = holding_time.total_seconds() / 60  # Convert peak timing to minutes

        coin_stats.append({
            'name': c['name'],
            'growth': growth,
            'drawdown': drawdown,
            'holding_time': peak_timing
        })

    # Calculate trust metrics
    all_growths = [stat['growth'] for stat in coin_stats]
    positive = [g for g in all_growths if g > 0]
    negative = [g for g in all_growths if g <= 0]
    trust = len(positive) / (len(positive) + len(negative)) if (len(positive) + len(negative)) > 0 else 0

    # Calculate additional statistics
    avg_growth = mean(all_growths) if all_growths else 0
    median_growth = median(all_growths) if all_growths else 0
    stddev_growth = stdev(all_growths) if len(all_growths) > 1 else 0
    avg_drawdown = mean([stat['drawdown'] for stat in coin_stats]) if coin_stats else 0
    avg_peak_timing = mean([stat['holding_time'] for stat in coin_stats]) if coin_stats else 0

    # Short-term, medium-term, and long-term win rates (example thresholds: 1 day, 1 week)
    short_term = [stat for stat in coin_stats if stat['holding_time'] <= 60]
    medium_term = [stat for stat in coin_stats if 24 < stat['holding_time'] <= 720]
    long_term = [stat for stat in coin_stats if stat['holding_time'] > 720]

    short_term_win_rate = len([s for s in short_term if s['growth'] > 0]) / len(short_term) if short_term else 0
    medium_term_win_rate = len([m for m in medium_term if m['growth'] > 0]) / len(medium_term) if medium_term else 0
    long_term_win_rate = len([l for l in long_term if l['growth'] > 0]) / len(long_term) if long_term else 0

    return {
        'coin_with_growth': coin_stats,
        'trust': trust,
        'average_growth': avg_growth,
        'median_growth': median_growth,
        'stddev_growth': stddev_growth,
        'average_drawdown': avg_drawdown,
        'average_peak_timing': avg_peak_timing,
        'short_term_win_rate': short_term_win_rate,
        'medium_term_win_rate': medium_term_win_rate,
        'long_term_win_rate': long_term_win_rate,
        'user': user
    }


def clearup_invalid_coins():
    coins = get_all()
    to_delete = list(filter(lambda x: x['user_id'] is None or "bot" in x['user_id'].lower(), coins))
    for deletion in to_delete:
        remove_entry(deletion['name'])
    return len(to_delete)

def should_buy(user_id, min_trust = 0.5):
    user_stats = get_user_statistics(user_id)

    if(float(user_stats['trust']) < float(min_trust)):
        return { 'buy': False }
    else:
        return {
            'buy': True,
            'peak_timing': user_stats['average_peak_timing'],
            'median_growth': user_stats['median_growth']
        }



from tinydb import TinyDB, Query
from enum import Enum
from datetime import datetime

class Status(Enum):
    HODL = 'HODL'
    BOUGHT = 'BOUGHT'
    SOLD = 'SOLD'

db = TinyDB('transactions.json')

statuses = ['HODL', 'BOUGHT', 'SOLD']

def save_entry(name, hashId, price, channel_id, user_id, expected_sell_time_in_minutes = 0, expected_growth = 0):
    current_time = str(datetime.now())
    db.insert({
        'name': name,
        'hash_id': hashId,
        'buying_price': price,
        'created_on': current_time,
        'highest_price': price,
        'highest_on': current_time,
        'lowest_price': price,
        'lowest_on': current_time,
        'status': Status.HODL.value,
        'growth': 0,
        'channel_id': channel_id,
        'expected_sell_time_in_minutes': expected_sell_time_in_minutes,
        'expected_growth': expected_growth,
        'user_id': user_id,
    })

def get_all():
    return db.all()

def get_entry(name):
    Coin = Query()
    return db.get(Coin.name == name)

def get_all_active():
    Coin = Query()
    return sorted(db.search(Coin.status == Status.HODL.value), key=lambda entry: entry['growth'], reverse=True)

def remove_entry(coin_name):
    Coin = Query()
    db.remove(Coin.name == coin_name)

def update_entry(name, value):
    Coin = Query()
    db.update(value, Coin.name == name)
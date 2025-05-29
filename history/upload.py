import os

from db.repositories import auctioneer
from utils import create_items_price_dict


def add_history(filename: str):
    with open(f'history/{filename}', 'r', encoding='utf-8') as input_f:
        data = input_f.read()
        items = create_items_price_dict(raw_text=data)
        auctioneer.add_prices_bulk(items=items)
        print(f'{os.path.splitext(filename)[0]} загружено...')


def init_history():
    history_files = [f for f in os.listdir('history') if f.endswith('.txt')]
    for f in history_files:
        add_history(filename=f)

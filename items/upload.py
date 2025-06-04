from db.repositories import auctioneer
from utils import correct_item_name


def init_items():
    with open(f'items/items_3.txt', 'r', encoding='utf-8') as input_f:
        data = input_f.read()
        rows = data.split('\n')
        items = []
        for r in rows:
            split_row = r.split(',')
            name = correct_item_name(",".join(split_row[:-3]))
            rarity = split_row[-3][1:-1]
            type_ = split_row[-1][1:-1]
            level = int(split_row[-2])
            items.append({
                'name': name,
                'rarity': rarity,
                'type': type_,
                'level': level
            })
        auctioneer.add_items_bulk(items=items)
        print('items загружено...')
        return items

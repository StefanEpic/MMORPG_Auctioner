import json
import os

from db.repositories import auctioneer


def upload_prof(file: str):
    with open(f'professions/{file}', 'r', encoding='utf-8') as input_f:
        data = json.loads(input_f.read())
        for d in data:
            quantity = data[d]["Количество"]
            try:
                quantity = int(quantity)
            except Exception as e:
                print(e)
                quantity = int([int(i) for i in quantity.split('-')][-1] / 2)
            materials = data[d].get("Материалы", None)

            if materials:
                materials = [i for i in materials.items()]
                auctioneer.add_recipe(item=str(d), count=quantity, materials=materials)


def init_professions():
    prof_files = [f for f in os.listdir('professions') if f.endswith('.json')]
    for f in prof_files:
        upload_prof(file=f)
        print(f'{os.path.splitext(f)[0]} загружено...')

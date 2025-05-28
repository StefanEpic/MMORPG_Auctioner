import json
import time

from utils import run

urls = [
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;50',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;100',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;150',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;200',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;250',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;300',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;350',
    'https://www.wowhead.com/wotlk/ru/skill=197/портняжное-дело#recipes;400',
]

for url in urls:
    with open('tailoring.json', 'r', encoding='utf-8') as new_file:
        data = new_file.read()
        data = json.loads(data)

    print(url)
    results = run(url)

    with open('tailoring.json', 'w', encoding='utf-8') as new_file:
        data.update(results)
        new_file.write(json.dumps(data, ensure_ascii=False, indent=4))

    time.sleep(5)

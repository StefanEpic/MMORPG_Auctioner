import json
import time

from utils import run

urls = [
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;50',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;100',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;150',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;200',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;250',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;300',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;350',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;400',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;450',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;500',
    'https://www.wowhead.com/wotlk/ru/skill=755/ювелирное-дело#recipes;550',
]

data = dict()
for url in urls:
    print(url)
    results = run(url)
    data.update(results)
    time.sleep(5)

with open('jewelcraft.json', 'w', encoding='utf-8') as new_file:
    new_file.write(json.dumps(data, ensure_ascii=False, indent=4))

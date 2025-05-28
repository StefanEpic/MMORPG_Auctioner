import json

from utils import run

with open(f'engineering.json', 'r', encoding='utf-8') as new_file:
    data = new_file.read()
    data = json.loads(data)

url = 'https://www.wowhead.com/wotlk/ru/skill=202/инженерное-дело#recipes:300'
results = run(url)

with open(f'engineering.json', 'w', encoding='utf-8') as new_file:
    data.update(results)
    new_file.write(json.dumps(data, ensure_ascii=False, indent=4))

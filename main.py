import json

from db.repositories import auctioneer

# with open('test_load.txt', 'r', encoding='utf-8') as input_f:
#     data = input_f.read()
#     rows = data.split('\n')
#     items = [r.split(',')[1].replace('"', '') for r in rows[1:]]
#     prices = [r.split(',')[0] for r in rows[1:]]
#     for i in zip(items, prices):
#         auctioneer.add_price(item=i[0], price=i[1])
#
# with open('engineering.json', 'r', encoding='utf-8') as input_f:
#     data = json.loads(input_f.read())
#     for d in data:
#         quantity = data[d]["Количество"]
#         try:
#             quantity = int(quantity)
#         except Exception as e:
#             print(e)
#             quantity = int([int(i) for i in quantity.split('-')][-1] / 2)
#         materials = data[d].get("Материалы", None)
#
#         if materials:
#             materials = [i for i in materials.items()]
#             auctioneer.add_recipe(item=str(d), count=quantity, materials=materials)

c = auctioneer.get_price_differences(10)
print(c)

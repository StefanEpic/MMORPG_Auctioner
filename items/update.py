from utils import correct_item_name

with open(f'items.txt', 'r', encoding='utf-8') as input_f:
    data = input_f.read()
    rows = data.split('\n')

with open(f'items_2.txt', 'r', encoding='utf-8') as input_f:
    data_2 = input_f.read()
    rows_2 = data_2.split('\n')

new = []
all_source_names = [correct_item_name(",".join(r.split(',')[:-3])) for r in rows]


def check(text: str) -> bool:
    count = 0
    for n in all_source_names:
        if text in n:
            count += 1

    if count == 1:
        return True
    return False


for r in rows:
    split_row = r.split(',')
    name = correct_item_name(",".join(split_row[:-3]))
    rarity = split_row[-3][1:-1]
    type_ = split_row[-1][1:-1]
    level = int(split_row[-2])
    new.append(r)

    for r2 in rows_2:
        if name in r2 and level not in [0, 1] and rarity in ['uncommon', 'rare', 'epic', 'legendary'] and check(name):
            new.append(f'"{r2}","{rarity}",{level},"{type_}"')

with open(f'items_3.txt', 'w', encoding='utf-8') as input_f:
    input_f.write("\n".join(new))

# with open(f'items_3.txt', 'r', encoding='utf-8') as input_f:
#     new_data = input_f.read()
#     new_rows = new_data.split('\n')
#     new_rows_names = [correct_item_name(",".join(i.split(',')[:-3])) for i in new_rows]
#
#     dubls = []
#     for n in new_rows_names:
#         if new_rows_names.count(n) != 1:
#             dubls.append(n)
#             print(n)
#
#     print(len(dubls))

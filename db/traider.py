from db.repositories import auctioneer


class Trader:
    @staticmethod
    def print_craft(min_profit: int, max_profit: int) -> None:
        recipes_for_craft = auctioneer.get_recipes_for_craft()
        for r in recipes_for_craft:
            if min_profit < r['Текущая выгода'] < max_profit and r['Текущая выгода'] > r['Средняя выгода']:
                print(f"{r['Рецепт']}:")
                print('\t', 'Выгода:', r['Текущая выгода'], 'г')
                print('\t', 'Цена:', r['Текущая стоимость продажи'], 'г')
                print('\t', 'Стоимость крафта:', r['Стоимость создания'], 'г')
                print('\t', 'Материалы:')
                for m in r['Материалы']:
                    print('\t', '\t', f"{m['Название']}: {m['Количество']} шт по {m['Цена']} г")

    @staticmethod
    def print_buy(min_profit: int, max_profit: int) -> None:
        items = auctioneer.get_price_differences()
        for i in items:
            if min_profit < i['Ниже средней цены на'] < max_profit:
                print(f"{i['Название']}:")
                print('\t', 'Выгода:', i['Ниже средней цены на'], 'г')
                print('\t', 'Цена:', i['Последняя цена'], 'г')
                print('\t', 'Средняя:', i['Средняя цена за месяц'], 'г')


trader = Trader()

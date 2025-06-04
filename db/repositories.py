from datetime import datetime, timedelta
from operator import and_
from typing import List, Tuple, Optional, Dict, Union

import pytz
from sqlalchemy import create_engine, func, select, desc
from sqlalchemy.orm import sessionmaker

from db.models import Base, Items, Prices, Recipes, ItemsQuantity


class DatabaseManager:
    def __init__(self, db_name: str = 'auctioneer.db'):
        self.engine = create_engine(f'sqlite:///{db_name}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def _create(self, model, **kwargs):
        session = self.Session()
        try:
            instance = model(**kwargs)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _read(self, model, filter_by=None, order_by=None, limit=None):
        session = self.Session()
        try:
            query = session.query(model)

            if filter_by is not None:
                query = query.filter_by(**filter_by)

            if order_by is not None:
                query = query.order_by(order_by)

            if limit is not None:
                query = query.limit(limit)

            return query.all()
        finally:
            session.close()

    def _update(self, model, filter_by, update_values):
        session = self.Session()
        try:
            result = session.query(model).filter_by(**filter_by).update(update_values)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _delete(self, model, filter_by):
        session = self.Session()
        try:
            result = session.query(model).filter_by(**filter_by).delete()
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _filter_by(self, model, **filter_by):
        session = self.Session()
        try:
            query = session.query(model).filter_by(**filter_by)
            return query.all()
        finally:
            session.close()


class Auctioneer(DatabaseManager):
    def __init__(self, db_name: str = 'auctioneer.db'):
        super().__init__(db_name=db_name)

    def add_item(self, name: str) -> Optional[Items]:
        try:
            return super()._create(model=Items, name=name)
        except Exception as e:
            print(e)

    def add_items_bulk(self, items: List[Dict[str, Union[str, int]]]):
        session = self.Session()
        try:
            items_for_bulk = [Items(name=i['name'], rarity=i['rarity'], type=i['type'], level=i['level']) for i in items]
            session.add_all(items_for_bulk)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка при массовом добавлении предметов: {e}")
        finally:
            session.close()

    def get_item_price(self, item_name: str) -> dict:
        session = self.Session()
        # Находим ID товара по имени
        item = session.execute(
            select(Items).where(Items.name == item_name)
        ).scalar_one_or_none()

        if item is None:
            return {item_name: None}

        # Получаем последнюю цену для этого товара
        last_price = session.execute(
            select(Prices.price)
            .where(Prices.item_id == item.id)
            .order_by(desc(Prices.date))
            .limit(1)
        ).scalar_one_or_none()

        return {item_name: round(last_price / 10000, 2)}

    def add_prices_bulk(self, items: Dict[str, int]) -> None:
        session = self.Session()
        try:
            # Получаем все существующие предметы за один запрос
            existing_names = {item.name: item.id for item in session.query(Items).all()}
            # Создаем новые предметы для тех, которых еще нет
            new_items = []
            for name in items.keys():
                if name not in existing_names:
                    new_item = Items(name=name)
                    new_items.append(new_item)
            if new_items:
                session.add_all(new_items)
                session.flush()  # Получаем ID для новых предметов
                existing_names.update({item.name: item.id for item in new_items})
            # Создаем записи цен
            prices = [
                Prices(item_id=existing_names[name], price=price)
                for name, price in items.items()
            ]
            session.add_all(prices)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка при массовом добавлении цен: {e}")
        finally:
            session.close()

    def _get_item_id(self, item: str) -> int:
        items = super()._filter_by(model=Items, name=item)
        if not items:
            item_id = self.add_item(name=item).id
        else:
            item_id = items[0].id
        return item_id

    def add_price(self, item: str, price: int) -> Optional[Prices]:
        try:
            item_id = self._get_item_id(item=item)
            return super()._create(model=Prices, item_id=item_id, price=price)
        except Exception as e:
            print(e)

    def _add_item_quantity(self, item: str, quantity: int, recipe_result_id: int = None,
                           recipe_materials_id: int = None) -> Optional[ItemsQuantity]:
        try:
            item_id = self._get_item_id(item=item)
            return super()._create(model=ItemsQuantity, item_id=item_id, quantity=quantity,
                                   recipe_result_id=recipe_result_id, recipe_materials_id=recipe_materials_id)
        except Exception as e:
            print(e)

    def add_recipe(self, item: str, count: int, materials: List[Tuple[str, int]]) -> Optional[Recipes]:
        try:
            # Проверяем есть ли уже рецепт
            recipes = super()._filter_by(model=Recipes, name=item)
            if recipes:
                return None
            # Проверяем есть ли такой предмет
            exist_item = super()._filter_by(model=Items, name=item)
            if not exist_item:
                return None

            try:
                recipe_id = super()._create(model=Recipes, name=item).id
            except Exception as e:
                print(e)
                return None

            self._add_item_quantity(item=item, quantity=count, recipe_result_id=recipe_id)
            for material in materials:
                self._add_item_quantity(item=material[0], quantity=material[1], recipe_materials_id=recipe_id)
        except Exception as e:
            print(e)

    def _get_avg_item_price(self, item: str) -> Optional[int]:
        session = self.Session()
        try:
            month_ago = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=30)
            price = session.query(func.avg(Prices.price)).join(Items, Prices.item_id == Items.id).filter(
                and_(Items.name == item, Prices.date >= month_ago)).scalar()
            if price:
                return int(price)
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()
        return None

    def get_price_differences(self):
        session = self.Session()
        try:
            month_ago = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=30)

            # Получаем все товары
            items = session.query(Items).all()
            results = []

            for item in items:
                # Последняя цена
                last_price = (
                    session.query(Prices.price)
                    .filter(Prices.item_id == item.id)
                    .order_by(Prices.date.desc())
                    .first()
                )

                # Средняя цена за месяц
                avg_price = (
                    session.query(func.avg(Prices.price))
                    .filter(
                        Prices.item_id == item.id,
                        Prices.date >= month_ago
                    )
                    .scalar()
                )

                if last_price and avg_price:
                    price_diff = last_price[0] - avg_price
                    results.append({
                        'Название': item.name,
                        'Последняя цена': round(last_price[0] / 10000, 2),
                        'Средняя цена за месяц': round(avg_price / 10000, 2),
                        'Ниже средней цены на': round(price_diff / 10000, 2),
                    })

            # Сортируем по абсолютной разнице (по убыванию)
            results.sort(key=lambda x: abs(x['Ниже средней цены на']))
            return results
        finally:
            session.close()

    def get_recipes_for_craft(self) -> List[Dict]:
        session = self.Session()

        latest_prices_subq = (
            select(
                Prices.item_id,
                func.max(Prices.date).label('max_date')
            )
            .group_by(Prices.item_id)
            .subquery()
        )

        latest_prices = (
            select(
                Prices.item_id,
                Prices.price
            )
            .join(
                latest_prices_subq,
                (Prices.item_id == latest_prices_subq.c.item_id) &
                (Prices.date == latest_prices_subq.c.max_date)
            )
        ).alias('latest_prices')

        # Получаем все рецепты с их материалами и результатами
        recipes = session.execute(
            select(
                Recipes.id,
                Recipes.name,
                ItemsQuantity.item_id,
                ItemsQuantity.quantity,
                latest_prices.c.price.label('item_price'),
                Items.name.label('item_name')  # Добавляем название предмета
            )
            .join(
                Recipes.materials
            )
            .join(
                Items,
                ItemsQuantity.item_id == Items.id
            )
            .join(
                latest_prices,
                ItemsQuantity.item_id == latest_prices.c.item_id,
                isouter=True
            )
        ).all()

        # Группируем материалы по рецептам и считаем стоимость крафта
        recipe_costs = {}
        for recipe in recipes:
            if recipe.id not in recipe_costs:
                recipe_costs[recipe.id] = {
                    'name': recipe.name,
                    'cost': 0,
                    'materials': []
                }

            if recipe.item_price is not None:
                material_cost = recipe.item_price * recipe.quantity
                recipe_costs[recipe.id]['cost'] += material_cost
                recipe_costs[recipe.id]['materials'].append({
                    'Название': recipe.item_name,  # Используем название вместо item_id
                    'Цена': round(recipe.item_price / 10000, 2),
                    'Количество': recipe.quantity,
                    'Всего': round(material_cost / 10000, 2)
                })

        # Получаем цены результатов рецептов
        recipe_results = session.execute(
            select(
                Recipes.id,
                latest_prices.c.price.label('result_price')
            )
            .join(
                Recipes.result
            )
            .join(
                latest_prices,
                ItemsQuantity.item_id == latest_prices.c.item_id,
                isouter=True
            )
        ).all()

        # Собираем итоговый список с расчетом прибыли
        profitable_recipes = []
        for recipe_id, result_price in recipe_results:
            if recipe_id not in recipe_costs:
                continue

            if result_price is None:
                continue

            cost = recipe_costs[recipe_id]['cost']
            profit = result_price - cost
            auction_commission = 0.05
            if profit > 0:
                avg_prise = self._get_avg_item_price(item=recipe_costs[recipe_id]['name'])
                avg_profit = avg_prise - cost
                profitable_recipes.append({
                    'Рецепт': recipe_costs[recipe_id]['name'],
                    'Текущая стоимость продажи': round(result_price / 10000, 2),
                    'Cредняя стоимость продажи': round(avg_prise / 10000, 2),
                    'Стоимость создания': round(cost / 10000, 2),
                    'Текущая выгода': round((profit - result_price * auction_commission) / 10000, 2),
                    'Средняя выгода': round((avg_profit - avg_prise * auction_commission) / 10000, 2),
                    'Материалы': recipe_costs[recipe_id]['materials']
                })

        # Сортируем по убыванию прибыли
        profitable_recipes.sort(key=lambda x: x['Текущая выгода'])

        return profitable_recipes


auctioneer = Auctioneer()

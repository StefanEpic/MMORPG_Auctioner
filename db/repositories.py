from datetime import datetime, timedelta
from operator import and_
from typing import List, Tuple, Optional

import pytz
from sqlalchemy import create_engine, func
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
            recipes = super()._filter_by(model=Recipes, name=item)
            if recipes:
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
        month_ago = datetime.now(pytz.timezone('Europe/Moscow')) - timedelta(days=30)
        price = session.query(func.avg(Prices.price)).join(Items, Prices.item_id == Items.id).filter(
            and_(Items.name == item, Prices.date >= month_ago)).scalar()
        if price:
            return int(price)
        return None

    def get_price_differences(self, filter_gold: int):
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
                    price_diff = int(avg_price - last_price[0])
                    results.append({
                        'Название': item.name,
                        # 'Последняя цена': last_price[0],
                        # 'Средняя цена за месяц': int(avg_price),
                        'Ниже средней цены на': round(price_diff / (filter_gold * 1000), 2),
                    })

            # Сортируем по абсолютной разнице (по убыванию)
            results.sort(key=lambda x: abs(x['Ниже средней цены на']), reverse=True)
            return[r for r in results if r['Ниже средней цены на'] > 0]
        finally:
            session.close()


auctioneer = Auctioneer()

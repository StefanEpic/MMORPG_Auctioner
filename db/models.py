from datetime import datetime
from typing import List, Optional

import pytz
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


class Items(Base):
    __tablename__ = 'items'
    name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)

    def __str__(self):
        return self.name


class Recipes(Base):
    __tablename__ = 'recipes'
    name: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    result: Mapped["ItemsQuantity"] = relationship(
        "ItemsQuantity",
        foreign_keys="[ItemsQuantity.recipe_result_id]",
        cascade="all, delete-orphan",
        back_populates="recipe_result",
        uselist=False,
        lazy="selectin"
    )
    materials: Mapped[List["ItemsQuantity"]] = relationship(
        "ItemsQuantity",
        foreign_keys="[ItemsQuantity.recipe_materials_id]",
        cascade="all, delete-orphan",
        back_populates="recipe_materials",
        lazy="selectin"
    )

    def __str__(self):
        return self.name


class ItemsQuantity(Base):
    __tablename__ = 'items_quantity'
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))
    recipe_result_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=True
    )
    recipe_result: Mapped[Optional["Recipes"]] = relationship(
        "Recipes",
        foreign_keys=[recipe_result_id],
        back_populates="result"
    )
    recipe_materials_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=True
    )
    recipe_materials: Mapped[Optional["Recipes"]] = relationship(
        "Recipes",
        foreign_keys=[recipe_materials_id],
        back_populates="materials"
    )
    quantity: Mapped[int] = mapped_column(nullable=False)


class Prices(Base):
    __tablename__ = 'prices'
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))
    price: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True),
                                           default=lambda: datetime.now(pytz.timezone('Europe/Moscow')))

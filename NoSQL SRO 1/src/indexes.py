"""Управление индексами каталога."""
from pymongo import ASCENDING, DESCENDING, TEXT


def create_indexes(db):
    p = db.products
    p.create_index([("sku", ASCENDING)], unique=True, name="uq_sku")
    # Категория (equality) + цена (sort/range): правило ESR
    p.create_index([("category", ASCENDING), ("price", ASCENDING)], name="ix_category_price")
    # Фильтр по характеристикам внутри категории
    p.create_index([("category", ASCENDING), ("specs.ram_gb", ASCENDING)], name="ix_category_ram")
    # Рейтинг внутри категории
    p.create_index([("category", ASCENDING), ("rating", DESCENDING)], name="ix_category_rating")
    # Полнотекстовый поиск
    p.create_index([("name", TEXT), ("brand", TEXT)], name="tx_name_brand")
    db.categories.create_index([("slug", ASCENDING)], unique=True, name="uq_slug")


def drop_indexes(db):
    """Удаляет все индексы, кроме _id (для замера «до индекса»)."""
    db.products.drop_indexes()
    db.categories.drop_indexes()

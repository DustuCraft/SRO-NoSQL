"""Демонстрационные запросы Q1-Q10. Q9 и Q10 - нетривиальные (aggregation pipeline)."""


def q1_by_sku(db, sku):
    """AP-1: карточка товара по SKU."""
    return db.products.find_one({"sku": sku}, {"_id": 0})


def q2_by_category(db, category, limit=10):
    """AP-2: список товаров категории (новинки первыми)."""
    return list(db.products.find({"category": category}, {"_id": 0})
                .sort("created_at", -1).limit(limit))


def q3_price_range(db, category, min_price, max_price, limit=20):
    """AP-3: фильтр по цене, сортировка по возрастанию цены."""
    return list(db.products.find(
        {"category": category, "price": {"$gte": min_price, "$lte": max_price}},
        {"_id": 0, "sku": 1, "name": 1, "brand": 1, "price": 1},
    ).sort("price", 1).limit(limit))


def q4_by_specs(db, min_ram_gb, max_price, brand=None):
    """AP-4: ноутбуки по характеристикам (RAM, цена, бренд)."""
    flt = {"category": "laptops", "specs.ram_gb": {"$gte": min_ram_gb}, "price": {"$lte": max_price}}
    if brand:
        flt["brand"] = brand
    return list(db.products.find(flt, {"_id": 0, "sku": 1, "name": 1, "specs": 1, "price": 1})
                .sort("price", 1))


def q5_avg_price_by_category(db):
    """AP-5: средняя цена по категориям."""
    return list(db.products.aggregate([
        {"$group": {"_id": "$category", "avg_price": {"$avg": "$price"}, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "category": "$_id", "count": 1,
                      "avg_price": {"$round": ["$avg_price", 2]}}},
        {"$sort": {"avg_price": -1}},
    ]))


def q6_text_search(db, text, limit=10):
    """AP-6: полнотекстовый поиск по названию и бренду."""
    return list(db.products.find(
        {"$text": {"$search": text}},
        {"_id": 0, "sku": 1, "name": 1, "price": 1, "score": {"$meta": "textScore"}},
    ).sort([("score", {"$meta": "textScore"})]).limit(limit))


def q7_top_rated(db, category, limit=5):
    """AP-7: топ по рейтингу в категории."""
    return list(db.products.find({"category": category}, {"_id": 0, "sku": 1, "name": 1, "rating": 1})
                .sort("rating", -1).limit(limit))


def q8_low_stock(db, threshold=5):
    """AP-8: товары с низким остатком."""
    return list(db.products.find({"stock": {"$lte": threshold}}, {"_id": 0, "sku": 1, "name": 1, "stock": 1})
                .sort("stock", 1))


def q9_brand_stats(db, category):
    """НЕТРИВИАЛЬНЫЙ 1: статистика цен и рейтинга по брендам внутри категории."""
    return list(db.products.aggregate([
        {"$match": {"category": category}},
        {"$group": {"_id": "$brand", "avg_price": {"$avg": "$price"},
                    "min_price": {"$min": "$price"}, "max_price": {"$max": "$price"},
                    "models": {"$sum": 1}, "avg_rating": {"$avg": "$rating"}}},
        {"$sort": {"avg_price": -1}},
        {"$project": {"_id": 0, "brand": "$_id", "models": 1,
                      "avg_price": {"$round": ["$avg_price", 2]},
                      "min_price": 1, "max_price": 1,
                      "avg_rating": {"$round": ["$avg_rating", 2]}}},
    ]))


def q10_price_segments(db):
    """НЕТРИВИАЛЬНЫЙ 2: ценовые сегменты ($bucket) + названия категорий ($lookup)."""
    return list(db.products.aggregate([
        {"$bucket": {
            "groupBy": "$price",
            "boundaries": [0, 100, 300, 700, 1500, 100000],
            "default": "other",
            "output": {"count": {"$sum": 1}, "avg_rating": {"$avg": "$rating"},
                       "categories": {"$addToSet": "$category"}},
        }},
        {"$lookup": {"from": "categories", "localField": "categories",
                     "foreignField": "slug", "as": "category_docs"}},
        {"$project": {"_id": 0, "segment_from": "$_id", "count": 1,
                      "avg_rating": {"$round": ["$avg_rating", 2]},
                      "category_names": "$category_docs.name"}},
    ]))

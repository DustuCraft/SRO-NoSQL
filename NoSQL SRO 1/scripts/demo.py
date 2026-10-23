"""Запуск всех демонстрационных запросов: python -m scripts.demo"""
from pprint import pprint
from src.db import get_db
from src import queries as q


def main():
    db = get_db()
    sku = db.products.find_one({}, {"sku": 1})["sku"]
    demos = [
        ("Q1 by SKU", lambda: q.q1_by_sku(db, sku)),
        ("Q2 category list", lambda: q.q2_by_category(db, "laptops", 3)),
        ("Q3 price range", lambda: q.q3_price_range(db, "smartphones", 200, 800, 5)),
        ("Q4 specs filter", lambda: q.q4_by_specs(db, 16, 2000)),
        ("Q5 avg price by category", lambda: q.q5_avg_price_by_category(db)),
        ("Q6 text search", lambda: q.q6_text_search(db, "Nexa")),
        ("Q7 top rated", lambda: q.q7_top_rated(db, "tv", 3)),
        ("Q8 low stock", lambda: q.q8_low_stock(db, 3)),
        ("Q9 brand stats (aggregation)", lambda: q.q9_brand_stats(db, "laptops")),
        ("Q10 price segments ($bucket+$lookup)", lambda: q.q10_price_segments(db)),
    ]
    for title, fn in demos:
        print(f"\n=== {title} ===")
        pprint(fn())


if __name__ == "__main__":
    main()

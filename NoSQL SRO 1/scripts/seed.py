"""Заполнение БД синтетическими данными: python -m scripts.seed [--count 60] [--reset]"""
import argparse
import random
from datetime import datetime, timedelta, timezone

from src.db import get_db
from src.indexes import create_indexes

CATEGORIES = [
    {"slug": "smartphones", "name": "Смартфоны"},
    {"slug": "laptops", "name": "Ноутбуки"},
    {"slug": "headphones", "name": "Наушники"},
    {"slug": "tv", "name": "Телевизоры"},
]
BRANDS = {
    "smartphones": ["Aurora", "Nexa", "Zenit", "Orbis"],
    "laptops": ["Aurora", "Nexa", "Kappa", "Lumen"],
    "headphones": ["Sonic", "Nexa", "Orbis"],
    "tv": ["Lumen", "Zenit", "Kappa"],
}
PRICE_RANGE = {"smartphones": (120, 1500), "laptops": (350, 2800),
               "headphones": (20, 450), "tv": (180, 2500)}


def specs_for(cat, rng):
    if cat == "smartphones":
        return {"ram_gb": rng.choice([4, 6, 8, 12]), "storage_gb": rng.choice([64, 128, 256, 512]),
                "screen_in": round(rng.uniform(5.5, 6.9), 1), "battery_mah": rng.choice([4000, 4500, 5000])}
    if cat == "laptops":
        return {"ram_gb": rng.choice([8, 16, 32, 64]), "storage_gb": rng.choice([256, 512, 1024]),
                "cpu": rng.choice(["i5", "i7", "Ryzen 5", "Ryzen 7"]), "screen_in": rng.choice([13.3, 14, 15.6, 17])}
    if cat == "headphones":
        return {"type": rng.choice(["in-ear", "over-ear"]), "wireless": rng.choice([True, False]),
                "battery_h": rng.choice([8, 20, 30, 40])}
    return {"diagonal_in": rng.choice([32, 43, 50, 55, 65]), "panel": rng.choice(["LED", "OLED", "QLED"]),
            "resolution": rng.choice(["FullHD", "4K"])}


def generate(count, rng=None, start=0):
    rng = rng or random.Random(42)
    now = datetime.now(timezone.utc)
    docs = []
    for i in range(start, start + count):
        cat = rng.choice(list(BRANDS))
        brand = rng.choice(BRANDS[cat])
        lo, hi = PRICE_RANGE[cat]
        docs.append({
            "sku": f"{cat[:3].upper()}-{i:07d}",
            "name": f"{brand} {cat[:-1].capitalize()} {rng.randint(100, 999)}",
            "brand": brand, "category": cat,
            "price": round(rng.uniform(lo, hi), 2), "currency": "USD",
            "stock": rng.randint(0, 100), "rating": round(rng.uniform(2.5, 5.0), 1),
            "specs": specs_for(cat, rng),
            "tags": rng.sample(["new", "sale", "bestseller", "eco", "premium"], k=2),
            "created_at": now - timedelta(days=rng.randint(0, 700)),
        })
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=60)
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()
    db = get_db()
    if args.reset:
        db.products.drop()
        db.categories.drop()
    create_indexes(db)
    db.categories.delete_many({})
    db.categories.insert_many(CATEGORIES)
    db.products.insert_many(generate(args.count))
    print(f"Inserted {args.count} products, {len(CATEGORIES)} categories into '{db.name}'")


if __name__ == "__main__":
    main()

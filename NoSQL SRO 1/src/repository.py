"""CRUD-операции каталога."""
from datetime import datetime, timezone


def create_product(db, product: dict):
    product = {**product, "created_at": datetime.now(timezone.utc)}
    return db.products.insert_one(product).inserted_id


def get_product(db, sku: str):
    return db.products.find_one({"sku": sku}, {"_id": 0})


def update_price(db, sku: str, new_price: float) -> bool:
    res = db.products.update_one(
        {"sku": sku},
        {"$set": {"price": new_price, "updated_at": datetime.now(timezone.utc)}},
    )
    return res.modified_count == 1


def update_stock(db, sku: str, delta: int) -> bool:
    return db.products.update_one({"sku": sku}, {"$inc": {"stock": delta}}).modified_count == 1


def delete_product(db, sku: str) -> bool:
    return db.products.delete_one({"sku": sku}).deleted_count == 1

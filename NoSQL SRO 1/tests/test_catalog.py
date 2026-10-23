"""Тесты (нужен запущенный MongoDB). Используется отдельная БД electronics_test."""
import pytest
from pymongo.errors import DuplicateKeyError

from src.db import get_db
from src.indexes import create_indexes
from src import queries as q, repository as repo
from scripts.seed import CATEGORIES, generate


@pytest.fixture()
def db():
    d = get_db("electronics_test")
    d.products.drop()
    d.categories.drop()
    create_indexes(d)
    d.categories.insert_many(CATEGORIES)
    d.products.insert_many(generate(60))
    yield d
    d.client.drop_database("electronics_test")


def test_seed_has_at_least_30_records(db):
    assert db.products.count_documents({}) >= 30


def test_crud_cycle(db):
    sku = "TEST-0001"
    repo.create_product(db, {"sku": sku, "name": "Test", "brand": "Nexa", "category": "tv",
                             "price": 100.0, "stock": 3, "rating": 4.0, "specs": {}})
    assert repo.get_product(db, sku)["price"] == 100.0
    assert repo.update_price(db, sku, 90.0)
    assert repo.get_product(db, sku)["price"] == 90.0
    assert repo.delete_product(db, sku)
    assert repo.get_product(db, sku) is None


def test_unique_sku(db):
    doc = db.products.find_one({}, {"_id": 0})
    with pytest.raises(DuplicateKeyError):
        db.products.insert_one(doc)


def test_price_filter_and_sort(db):
    res = q.q3_price_range(db, "laptops", 500, 1500)
    prices = [r["price"] for r in res]
    assert all(500 <= p <= 1500 for p in prices)
    assert prices == sorted(prices)


def test_avg_price_aggregation(db):
    res = {r["category"]: r for r in q.q5_avg_price_by_category(db)}
    docs = list(db.products.find({"category": "laptops"}))
    expected = round(sum(d["price"] for d in docs) / len(docs), 2)
    assert res["laptops"]["avg_price"] == expected


def test_query_uses_index(db):
    plan = db.command("explain", {"find": "products",
                                  "filter": {"category": "laptops", "price": {"$gte": 500}}},
                      verbosity="queryPlanner")
    assert "IXSCAN" in str(plan["queryPlanner"]["winningPlan"])


def test_price_segments_sum_equals_total(db):
    total = sum(s["count"] for s in q.q10_price_segments(db))
    assert total == db.products.count_documents({})

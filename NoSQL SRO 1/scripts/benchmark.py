"""Сравнение запросов ДО и ПОСЛЕ индексов: python -m scripts.benchmark [--count 100000]"""
import argparse
import time

from src.db import get_db
from src.indexes import create_indexes, drop_indexes
from scripts.seed import CATEGORIES, generate

QUERIES = {
    "price range (laptops 500-1000, sort price)": (
        {"category": "laptops", "price": {"$gte": 500, "$lte": 1000}}, [("price", 1)]),
    "specs (laptops ram>=16, price<=1500)": (
        {"category": "laptops", "specs.ram_gb": {"$gte": 16}, "price": {"$lte": 1500}}, [("price", 1)]),
    "top rated smartphones": ({"category": "smartphones"}, [("rating", -1)]),
    "by sku": ({"sku": "LAP-0000010"}, None),
}


def stages(plan):
    out = [plan.get("stage")]
    if "inputStage" in plan:
        out += stages(plan["inputStage"])
    for child in plan.get("inputStages", []):
        out += stages(child)
    return [s for s in out if s]


def measure(coll, flt, sort, runs=15):
    def cursor():
        c = coll.find(flt)
        return c.sort(sort) if sort else c

    cmd = {"find": coll.name, "filter": flt}
    if sort:
        cmd["sort"] = dict(sort)
    info = coll.database.command("explain", cmd, verbosity="executionStats")
    st = info["executionStats"]
    plan = info["queryPlanner"]["winningPlan"]
    t0 = time.perf_counter()
    for _ in range(runs):
        list(cursor())
    avg_ms = (time.perf_counter() - t0) / runs * 1000
    return {"plan": "/".join(stages(plan)), "examined": st["totalDocsExamined"],
            "returned": st["nReturned"], "avg_ms": round(avg_ms, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=100_000)
    args = ap.parse_args()
    db = get_db(get_db().name + "_bench")
    db.products.drop()
    db.categories.drop()
    db.categories.insert_many(CATEGORIES)
    docs = generate(args.count)
    for i in range(0, len(docs), 10_000):
        db.products.insert_many(docs[i:i + 10_000])
    print(f"Bench DB '{db.name}': {args.count} documents\n")

    drop_indexes(db)
    before = {n: measure(db.products, f, s) for n, (f, s) in QUERIES.items()}
    create_indexes(db)
    after = {n: measure(db.products, f, s) for n, (f, s) in QUERIES.items()}

    print(f"{'query':45} {'phase':7} {'plan':32} {'examined':>9} {'ms':>8}")
    for n in QUERIES:
        for phase, res in (("before", before), ("after", after)):
            r = res[n]
            print(f"{n:45} {phase:7} {r['plan']:32} {r['examined']:>9} {r['avg_ms']:>8}")
        print(f"{'':45} speedup x{before[n]['avg_ms'] / max(after[n]['avg_ms'], 0.01):.1f}\n")


if __name__ == "__main__":
    main()

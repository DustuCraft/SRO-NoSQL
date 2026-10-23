# Каталог электроники с быстрым поиском (MongoDB)

Мини-проект СРО по дисциплине «Проектирование и применение NoSQL-технологий», вариант 1.

Возможности: CRUD карточек, фильтрация по цене и характеристикам, агрегации (средняя цена, статистика по брендам,
ценовые сегменты), полнотекстовый поиск, сравнение запросов до и после индексов.

## Запуск
```bash
docker compose up -d                 # MongoDB 7
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # Windows: copy .env.example .env

python -m scripts.seed --reset --count 60   # 60 синтетических товаров + индексы
python -m scripts.demo                       # 10 демонстрационных запросов
python -m scripts.benchmark --count 100000   # до/после индексов (explain + время)
pytest -v                                    # тесты
```

## Структура
```
src/          db.py, indexes.py, repository.py (CRUD), queries.py (Q1-Q10)
scripts/      seed.py, demo.py, benchmark.py
tests/        test_catalog.py
docs/         requirements.md, ADR.md, architecture.png, report.pdf, presentation.pdf
```

## Модель данных
`products`: `sku` (уникальный), `name`, `brand`, `category` (slug), `price`, `stock`, `rating`, `specs` (вложенный
документ, зависит от категории), `tags`, `created_at`. `categories`: `slug`, `name`.

## Индексы
| Индекс | Назначение |
|--------|-----------|
| `uq_sku` | AP-1, уникальность |
| `ix_category_price` | AP-2, AP-3 (equality + sort/range) |
| `ix_category_ram` | AP-4 |
| `ix_category_rating` | AP-7 |
| `tx_name_brand` | AP-6 (text) |

## Документы
Отчёт: `docs/report.pdf` — ссылка TODO. Презентация: `docs/presentation.pdf` — ссылка TODO.
Требования и Access Patterns: `docs/requirements.md`. ADR: `docs/ADR.md`.

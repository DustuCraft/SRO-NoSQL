"""Подключение к MongoDB. Параметры берутся из .env (см. .env.example)."""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_db(name: str | None = None):
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = name or os.getenv("MONGO_DB", "electronics")
    return MongoClient(uri, serverSelectionTimeoutMS=3000)[db_name]

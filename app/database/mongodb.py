from pymongo import MongoClient

from app.core.config import settings


client = MongoClient(settings.MONGO_URI)

db = client[settings.DB_NAME]

violations_collection = db["violations"]

analytics_collection = db["analytics"]

vehicles_collection = db["vehicles"]
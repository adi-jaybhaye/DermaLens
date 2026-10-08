import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config.settings import settings


client = MongoClient(
    settings.mongodb_uri,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
)

database = client[settings.mongodb_database]


def check_database_connection() -> bool:
    try:
        client.admin.command("ping")
        return True
    except PyMongoError:
        return False
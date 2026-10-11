import certifi
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from app.config.settings import settings

logger = logging.getLogger(__name__)

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


def init_db_indexes() -> None:
    """Create essential performance and uniqueness indexes in MongoDB."""
    try:
        # Users: Unique index on email
        database.users.create_index([("email", ASCENDING)], unique=True)

        # Assessment Sessions: User ID for authorization queries, created_at for sorting history
        database.assessment_sessions.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

        # Assessment Images: Fast lookup by assessment_id
        database.assessment_images.create_index([("assessment_id", ASCENDING)])
        database.assessment_images.create_index([("assessment_id", ASCENDING), ("view", ASCENDING)])
        logger.info("MongoDB indexes verified successfully.")
    except Exception as e:
        logger.warning(f"Could not initialize MongoDB indexes: {e}")
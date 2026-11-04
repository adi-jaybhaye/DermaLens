import certifi
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, ConfigurationError

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Configure dnspython with fallback public DNS (Google, Cloudflare)
# Windows local router DNS often drops or times out on SRV record queries for mongodb+srv://
try:
    import dns.resolver
    resolver = dns.resolver.get_default_resolver()
    public_dns = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
    current_dns = [s for s in resolver.nameservers if s not in public_dns]
    resolver.nameservers = public_dns + current_dns
except Exception as e:
    logger.debug(f"Could not adjust DNS resolver nameservers: {e}")

def _init_mongo_client() -> MongoClient:
    """Initialize MongoClient with SRV resolution and resilient direct cluster fallback."""
    try:
        c = MongoClient(
            settings.mongodb_uri,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        return c
    except (ConfigurationError, PyMongoError) as exc:
        if settings.mongodb_direct_fallback_uri:
            logger.warning(
                f"Failed to connect via SRV URI ({exc}). Attempting direct replica-set cluster connection from settings..."
            )
            return MongoClient(
                settings.mongodb_direct_fallback_uri,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
        raise exc


client = _init_mongo_client()
database = client[settings.mongodb_database]


def check_database_connection() -> bool:
    try:
        client.admin.command("ping")
        return True
    except (PyMongoError, Exception):
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

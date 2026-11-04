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
    """Initialize MongoClient with adaptive TLS, SRV resolution, and resilient direct cluster fallback."""
    uri = settings.mongodb_uri
    is_srv = uri.startswith("mongodb+srv://")
    has_tls = is_srv or "tls=true" in uri.lower() or "ssl=true" in uri.lower()

    client_kwargs = {
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 5000,
    }
    if has_tls:
        client_kwargs["tls"] = True
        client_kwargs["tlsCAFile"] = certifi.where()

    try:
        c = MongoClient(uri, **client_kwargs)
        return c
    except (ConfigurationError, PyMongoError) as exc:
        if settings.mongodb_direct_fallback_uri:
            logger.warning(
                f"Failed to connect via primary URI ({exc}). Attempting direct replica-set cluster connection from settings..."
            )
            fallback_uri = settings.mongodb_direct_fallback_uri
            fallback_has_tls = (
                fallback_uri.startswith("mongodb+srv://")
                or "tls=true" in fallback_uri.lower()
                or "ssl=true" in fallback_uri.lower()
            )
            fb_kwargs = {
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000,
            }
            if fallback_has_tls:
                fb_kwargs["tls"] = True
                fb_kwargs["tlsCAFile"] = certifi.where()
            return MongoClient(fallback_uri, **fb_kwargs)
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

import os
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb://localhost:27017")
if DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("sqlite"):
    logger.warning("DATABASE_URL is set to a SQL database but backend expects MongoDB. Falling back to localhost MongoDB.")
    DATABASE_URL = "mongodb://localhost:27017"

client = MongoClient(DATABASE_URL)
# Handle connecting to the correct database (Render MongoDB Atlas URIs usually include the DB name or rely on default)
db = client.get_default_database("library_ai_pro") if "localhost" in DATABASE_URL or "?" not in DATABASE_URL else client.get_database()
if db.name == 'test':
    db = client.get_database("library_ai_pro")

def get_db():
    yield db

# Utility for auto-incrementing integer IDs to keep frontend compatibility
def get_next_sequence_value(sequence_name: str) -> int:
    sequence_document = db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return sequence_document["sequence_value"]

import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = "lottery_db"

client: MongoClient | None = None
db: Database | None = None

def connect_db():
    global client, db
    if client is None:
        try:
            print(f"Attempting to connect to MongoDB at {MONGO_URI}")
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
            db = client[DB_NAME]
            print(f"Successfully connected to MongoDB. Using database: {DB_NAME}")
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            client = None
            db = None
            raise ConnectionFailure(f"Could not connect to MongoDB: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during MongoDB connection: {e}")
            client = None
            db = None
            raise Exception(f"An unexpected error occurred: {e}")


def get_db() -> Database:
    if db is None:
        connect_db()
    if db is None: # Still None after trying to connect
        raise ConnectionFailure("Database not connected. Call connect_db() first or check connection.")
    return db

def close_db_connection():
    global client
    if client:
        client.close()
        client = None
        print("MongoDB connection closed.")

# Connect on import - for FastAPI, dependency injection is better,
# but for this structure, we'll connect and handle errors.
# In a FastAPI app, you'd typically use startup/shutdown events.
try:
    connect_db()
except Exception as e:
    # Allow app to start, but log that DB is not available.
    # Endpoints trying to use get_db() will fail until DB is up.
    print(f"Failed to connect to database on initial load: {e}")

# Example of how to get collections (optional here, can be done in modules)
# def get_tickets_collection():
#     return get_db().tickets

# def get_draws_collection():
#     return get_db().draws

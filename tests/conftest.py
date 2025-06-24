import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient as MockMongoClient
# from unittest.mock import patch # monkeypatch is generally preferred with pytest

# Import your FastAPI application
from app import app
import database # Import your database module to patch it

@pytest.fixture(scope="function")
def test_client(monkeypatch):
    """
    Test client fixture that directly patches database.connect_db
    to use mongomock.
    """
    # Create a single MockMongoClient instance for the test function
    mock_mongo_client_instance = MockMongoClient()

    # This is the function that will replace database.connect_db
    def mock_connect_db_logic():
        # print("Attempting to connect with MOCK connect_db_logic...") # Debug print
        try:
            # Set the global client and db in the 'database' module directly
            database.client = mock_mongo_client_instance
            # Ensure server is available (mongomock is always "available")
            database.client.admin.command('ismaster') # A lightweight command
            database.db = database.client[database.DB_NAME + "_test"] # Use a distinct test DB name
            # print(f"Mock DB '{database.db.name}' set up with {type(database.client)}")
        except Exception as e:
            # print(f"Mock connect_db_logic failed: {e}")
            # If this fails, tests will likely fail when trying to access db
            database.client = None
            database.db = None
            raise # Re-raise the exception to make it clear if mock setup failed

    # Before each test, patch database.connect_db
    monkeypatch.setattr(database, 'connect_db', mock_connect_db_logic)

    # Also, ensure that if get_db() was called before and failed, it can retry.
    # Resetting these ensures get_db will call our patched connect_db.
    database.client = None
    database.db = None

    # Yield the TestClient. FastAPI's TestClient will run startup events,
    # which should now call our mock_connect_db_logic.
    with TestClient(app) as client_instance:
        yield client_instance

    # After each test, clear all collections in the mock database for isolation
    if database.db is not None and isinstance(database.client, MockMongoClient):
        # print(f"Clearing mock DB: {database.db.name}")
        for collection_name in database.db.list_collection_names():
            database.db[collection_name].delete_many({})
            # print(f"Cleared collection: {collection_name}")

    # Reset globals in database module again to ensure clean state for next test if any
    database.client = None
    database.db = None
    # monkeypatch automatically undoes the setattr for 'connect_db'

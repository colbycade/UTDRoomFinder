import pytest
import os
import json
from unittest.mock import patch

# Set environment variable before importing the app to use mock database
os.environ['DB_TYPE'] = 'mock'

from app import app as flask_app # Rename to avoid conflict with pytest 'app' fixture
from app import db as mock_db  # Import to directly verify database interactions
    

# Use Pytest Fixtures for managing testing context

@pytest.fixture(scope='module') # Only create the app once per test module
def app():
    flask_app.config.update({"TESTING": True})
    yield flask_app

# Test client to simulate requests to the app
@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True) # Runs automatically for EVERY test function
def reset_mock_db_state():
    mock_db.initialize_db(False) # clear the mock database
    yield # test function runs here

# Unit Tests for app.py

# Test GET /
def test_search_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data
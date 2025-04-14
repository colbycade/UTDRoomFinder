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
    mock_db.clear_db() # clear the mock database
    yield # test function runs here

# Constants for testing
DATE = "2025-04-14"
BUILDING = "TestBuilding"
ROOM = "T.101"
SEARCH_START_TIME = "12:00"
SEARCH_END_TIME = "14:00"
MIN_DURATION = "30"
EVENT_START_TIME = "10:00"
EVENT_END_TIME = "12:00"
EVENT_TITLE = "Test Event"
NOTES = "Test Notes"
MOCK_ROOM_DATA = [
    {
        "building": BUILDING,
        "room": ROOM,
        "schedule": {
            DATE: [
                {
                    "start_time": EVENT_START_TIME,
                    "end_time": EVENT_END_TIME,
                    "status": "Scheduled",
                    "event_title": EVENT_TITLE,
                    "notes": NOTES
                }
            ]
        }
    }
]


# Unit Tests for app.py

# Test GET /
def test_search_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Find a Room at UTD" in response.data

# Test GET /map
def test_map_page_loads(client):
    response = client.get('/map')
    assert response.status_code == 200
    assert b"Campus Map" in response.data

# Test POST /results search with no parameters
def test_results_page_loads(client):
    form_data = {
        'building': "Any Building",
        'room': "Any Room",
        'date': DATE,
        'start_time': '',
        'end_time': '',
        'duration': ''
    }
    response = client.post('/results', data=form_data)
    assert response.status_code == 200
    assert b"Available Rooms" in response.data
    assert b"No rooms available" in response.data # no results

# Test search with specific room
def test_search_room(client):
    mock_db.rooms = MOCK_ROOM_DATA
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': '',
        'end_time': '',
        'duration': ''
    }
    response = client.post('/results', data=form_data)
    print(response.data)
    assert BUILDING.encode('utf-8') in response.data
    assert ROOM.encode('utf-8') in response.data
    assert b"View Schedule" in response.data # room appears in results

# Test search with specific time range and duration
def test_search_time(client):
    mock_db.rooms = MOCK_ROOM_DATA
    form_data = {
        'building': BUILDING,
        'room': ROOM,
        'date': DATE,
        'start_time': SEARCH_START_TIME,
        'end_time': SEARCH_END_TIME,
        'duration': MIN_DURATION
    }
    response = client.post('/results', data=form_data)
    assert SEARCH_START_TIME.encode('utf-8') in response.data
    assert SEARCH_END_TIME.encode('utf-8') in response.data
    assert MIN_DURATION.encode('utf-8') in response.data
    assert b"View Schedule" in response.data # room appears in results
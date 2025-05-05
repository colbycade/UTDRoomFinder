# Written by Colby
# Integration tests for MongoDB database operations

import pytest
import os
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure
from mongodb import MongoDatabase

TEST_SEMESTER_COLLECTION = "test_semester_data"

# --- Test Data ---
SAMPLE_ROOM_1 = {
    "building": "ECSS",
    "room": "2.101",
    "schedule": {
        "2025-09-01": [
            {"start_time": "09:00", "end_time": "10:30", "status": "Scheduled", "event_title": "CS 101", "notes": ""},
            {"start_time": "11:00", "end_time": "12:00", "status": "Scheduled", "event_title": "CS 102 Lab", "notes": ""},
            {"start_time": "14:00", "end_time": "15:00", "status": "Cancelled", "event_title": "Meeting", "notes": "Cancelled due to conflict"},
        ],
        "2025-09-02": [
            {"start_time": "10:00", "end_time": "11:30", "status": "User Reported", "event_title": "Study Group", "notes": "My study group"}
        ]
    }
}
SAMPLE_ROOM_2 = {
    "building": "ECSS",
    "room": "2.102",
    "schedule": {
        "2025-09-01": [
            {"start_time": "10:00", "end_time": "11:00", "status": "Scheduled", "event_title": "CS 201", "notes": ""}
        ]
    }
}
SAMPLE_ROOM_3 = {
    "building": "JSOM",
    "room": "1.101",
    "schedule": {}
}

# --- Pytest Fixtures ---

@pytest.fixture(scope="module") # Module scope to share the same db_instance across all tests
def db_instance():
    print("Setting up Database Connection")

    # Check if credentials are set
    load_dotenv()
    if not os.environ.get("mongodb_user") or not os.environ.get("mongodb_pwd"):
         pytest.fail("Missing 'mongodb_user' or 'mongodb_pwd' environment variables. Cannot run integration tests.")

    database = MongoDatabase()
    database.semester_collection = TEST_SEMESTER_COLLECTION
    
    # Initialize connection
    try:
        initialized = database.initialize_db()
        if not initialized or database.client is None or database.db is None or database.collection is None:
             pytest.fail("Failed to initialize database connection.")
    except Exception as e:
        pytest.fail(f"Error during database setup: {e}")

    yield database # Provide the db instance to test_db

    # Teardown after all tests
    if database.client:
        try:
            database.db.drop_collection(TEST_SEMESTER_COLLECTION)
        except Exception as e:
            print(f"Error dropping test collection: {e}")
        database.client.close()
        print("MongoDB connection closed.")

@pytest.fixture(scope="function") # Reset the database state before each test function
def test_db(db_instance):
    collection = db_instance.collection
    
    # Clear the collection before each test
    collection.drop()

    # Insert fresh sample data
    try:
        collection.insert_many([SAMPLE_ROOM_1.copy(), SAMPLE_ROOM_2.copy(), SAMPLE_ROOM_3.copy()])
        # print("Sample data inserted.")
    except Exception as e:
        pytest.fail(f"Failed to insert sample data: {e}")
        
    yield db_instance # pass the db instance to test functions

# --- Test Functions ---
def test_initialize_db(db_instance):
    """Verify that the database connection is established"""
    assert db_instance.client is not None
    assert db_instance.db is not None
    assert db_instance.collection is not None
    assert db_instance.collection.name == TEST_SEMESTER_COLLECTION
    try:
        db_instance.client.admin.command('ping')
    except ConnectionFailure:
        pytest.fail("Database connection check (ping) failed.")

def test_get_room_found(test_db):
    """Test retrieving an existing room"""
    room = test_db.get_room("ECSS", "2.101")
    assert room is not None
    assert room["building"] == "ECSS"
    assert room["room"] == "2.101"
    assert "schedule" in room

def test_get_room_not_found(test_db):
    """Test retrieving a room that doesn't exist"""
    room = test_db.get_room("NonExistent", "123")
    assert room is None

def test_get_buildings(test_db):
    """Test retrieving the list of unique buildings"""
    buildings = test_db.get_buildings()
    assert len(buildings) == 2
    assert "ECSS" in buildings
    assert "JSOM" in buildings

def test_get_rooms_by_building(test_db):
    """Test retrieving the dictionary mapping buildings to rooms"""
    rooms_by_building = test_db.get_rooms_by_building()
    assert "ECSS" in rooms_by_building
    assert "JSOM" in rooms_by_building
    assert sorted(rooms_by_building["ECSS"]) == ["2.101", "2.102"]
    assert rooms_by_building["JSOM"] == ["1.101"]

def test_add_event_success_existing_room(test_db):
    """Test adding a valid event to an existing room"""
    result = test_db.add_event("ECSS", "2.102", "2025-09-01", "14:00", "15:00", "New Meeting", "Notes here", "User Reported")
    assert result is True
    
    # Verify the event was added
    room = test_db.get_room("ECSS", "2.102")
    assert room is not None
    schedule = room.get("schedule", {}).get("2025-09-01", [])
    assert len(schedule) == 2 # original event + new event
    
    new_event_found = False
    for event in schedule:
        if event["start_time"] == "14:00" and event["end_time"] == "15:00":
            assert event["event_title"] == "New Meeting"
            assert event["notes"] == "Notes here"
            assert event["status"] == "User Reported"
            new_event_found = True
            break
    assert new_event_found

def test_add_event_overlap(test_db):
    """Test adding an event that overlaps with an existing one"""
    # Overlaps with ECSS/2.101 09:00-10:30 on 2025-09-01
    result = test_db.add_event("ECSS", "2.101", "2025-09-01", "10:00", "11:00")
    assert result == "Event overlaps with an existing event"

    # Verify no event was added
    room = test_db.get_room("ECSS", "2.101")
    schedule = room.get("schedule", {}).get("2025-09-01", [])
    assert len(schedule) == 3 # Should remain unchanged from sample data

def test_add_event_overlap_with_cancelled(test_db):
    """Test adding an event that overlaps ONLY with a cancelled event (should succeed)"""
     # Overlaps with ECSS/2.101 14:00-15:00 (Cancelled) on 2025-09-01
    result = test_db.add_event("ECSS", "2.101", "2025-09-01", "14:30", "15:30")
    assert result is True

    # Verify the event was added
    room = test_db.get_room("ECSS", "2.101")
    schedule = room.get("schedule", {}).get("2025-09-01", [])
    assert len(schedule) == 4 # Original 3 + new one
    new_event_found = any(e["start_time"] == "14:30" for e in schedule)
    assert new_event_found

def test_add_event_invalid_time(test_db):
    """Test adding an event where start time is not before end time"""
    result_same_time = test_db.add_event("ECSS", "2.101", "2025-09-01", "10:00", "10:00")
    assert result_same_time == "Start time must be before end time"
    result_start_after_end = test_db.add_event("ECSS", "2.101", "2025-09-01", "11:00", "10:00")
    assert result_start_after_end == "Start time must be before end time"

def test_remove_user_event_success(test_db):
    """Test removing an existing user-reported event"""
    # Add a user event first to be sure
    test_db.add_event("JSOM", "1.101", "2025-09-05", "13:00", "14:00", status="User Reported")
    
    result = test_db.remove_user_event("JSOM", "1.101", "2025-09-05", "13:00", "14:00")
    assert result is True

    # Verify it's removed
    room = test_db.get_room("JSOM", "1.101")
    schedule = room.get("schedule", {}).get("2025-09-05", [])
    assert not any(e["start_time"] == "13:00" for e in schedule)

def test_remove_user_event_not_found(test_db):
    """Test removing a user event that doesn't exist"""
    result = test_db.remove_user_event("ECSS", "2.101", "2025-09-01", "15:00", "16:00") # Time doesn't exist
    assert result is False

def test_remove_user_event_wrong_status(test_db):
    """Test trying to remove a scheduled event (should fail)"""
    # Try removing CS 101 (Scheduled)
    result = test_db.remove_user_event("ECSS", "2.101", "2025-09-01", "09:00", "10:30")
    assert result is False

    # Verify it wasn't removed
    room = test_db.get_room("ECSS", "2.101")
    schedule = room.get("schedule", {}).get("2025-09-01", [])
    assert any(e["start_time"] == "09:00" and e["status"] == "Scheduled" for e in schedule)

def test_cancel_event_success(test_db):
    """Test cancelling a scheduled event"""
    result = test_db.cancel_event("ECSS", "2.101", "2025-09-01", "09:00", "10:30", notes="Test cancellation")
    assert result is True

    # Verify status and notes
    room = test_db.get_room("ECSS", "2.101")
    schedule = room.get("schedule", {}).get("2025-09-01", [])
    cancelled_event_found = False
    for event in schedule:
        if event["start_time"] == "09:00":
            assert event["status"] == "Cancelled"
            assert "Test cancellation" in event["notes"]
            assert "User reported event as cancelled." in event["notes"]
            cancelled_event_found = True
            break
    assert cancelled_event_found

def test_cancel_event_not_found(test_db):
    """Test cancelling an event that doesn't exist"""
    result = test_db.cancel_event("ECSS", "2.101", "2025-09-01", "15:00", "16:00")
    assert result is False

def test_cancel_event_wrong_status(test_db):
    """Test cancelling a user-reported or already cancelled event (should fail)"""
    # Try cancelling user event
    result_user = test_db.cancel_event("ECSS", "2.101", "2025-09-02", "10:00", "11:30")
    assert result_user is False

    # Try cancelling already cancelled event
    result_cancelled = test_db.cancel_event("ECSS", "2.101", "2025-09-01", "14:00", "15:00")
    assert result_cancelled is False

def test_uncancel_event_success(test_db):
    """Test un-cancelling a cancelled event"""
    # Use the pre-cancelled event from sample data
    result = test_db.uncancel_event("ECSS", "2.101", "2025-09-01", "14:00", "15:00", notes="Test un-cancellation")
    assert result is True

    # Verify status and notes
    room = test_db.get_room("ECSS", "2.101")
    schedule = room.get("schedule", {}).get("2025-09-01", [])
    uncancelled_event_found = False
    for event in schedule:
        if event["start_time"] == "14:00":
            assert event["status"] == "Scheduled"
            assert "Test un-cancellation" in event["notes"]
            assert "User Confirmed." in event["notes"]
            uncancelled_event_found = True
            break
    assert uncancelled_event_found

def test_uncancel_event_not_found(test_db):
    """Test un-cancelling an event that doesn't exist"""
    result = test_db.uncancel_event("ECSS", "2.101", "2025-09-01", "15:00", "16:00")
    assert result is False

def test_uncancel_event_wrong_status(test_db):
    """Test un-cancelling a scheduled or user-reported event (should fail)"""
    # Try un-cancelling scheduled event
    result_scheduled = test_db.uncancel_event("ECSS", "2.101", "2025-09-01", "09:00", "10:30")
    assert result_scheduled is False

    # Try un-cancelling user event
    result_user = test_db.uncancel_event("ECSS", "2.101", "2025-09-02", "10:00", "11:30")
    assert result_user is False

def test_get_next_availability_found(test_db):
    """Test finding the next available slot"""
    # Gap between 10:30 and 11:00 on 2025-09-01 in ECSS/2.101
    next_avail = test_db.get_next_availability_on_date("ECSS", "2.101", "2025-09-01", start_time="09:00", end_time="12:00", min_duration=15)
    assert next_avail == "10:30 - 11:00" # 30 min duration >= 15

    # Gap after 12:00 (cancelled event at 14:00 doesn't count)
    next_avail_later = test_db.get_next_availability_on_date("ECSS", "2.101", "2025-09-01", start_time="12:00", end_time="16:00", min_duration=60)
    assert next_avail_later == "12:00 - 16:00" # Gap until end_time

def test_get_next_availability_not_found(test_db):
    """Test when no slot meets the minimum duration"""
    # Gap is 10:30-11:00 (30 mins)
    next_avail = test_db.get_next_availability_on_date("ECSS", "2.101", "2025-09-01", start_time="09:00", end_time="12:00", min_duration=45)
    assert next_avail is None

def test_get_next_availability_empty_room(test_db):
    """Test finding availability in an empty room"""
    next_avail = test_db.get_next_availability_on_date("JSOM", "1.101", "2025-09-01", start_time="09:00", end_time="17:00", min_duration=30)
    assert next_avail == "09:00 - 17:00"

def test_get_next_availability_no_schedule_for_date(test_db):
    """Test finding availability when the date has no schedule"""
    next_avail = test_db.get_next_availability_on_date("ECSS", "2.101", "2025-12-25", start_time="09:00", end_time="17:00", min_duration=30)
    assert next_avail == "09:00 - 17:00"

def test_get_rooms_with_sufficient_gap_found(test_db):
    """Test finding rooms that have a sufficient gap"""
    # ECSS/2.101 has 10:30-11:00 (30m) and 12:00-end (long) gaps on 2025-09-01 (ignoring cancelled)
    # ECSS/2.102 has 00:00-10:00 and 11:00-end gaps on 2025-09-01
    # JSOM/1.101 is fully available on 2025-09-01
    
    # Find rooms with at least 60 min gap
    free_rooms = test_db.get_rooms_with_sufficient_gap(None, None, "2025-09-01", "08:00", "18:00", min_duration=60)
    
    buildings_rooms = {(r['building'], r['room']) for r in free_rooms}
    assert len(free_rooms) == 3 # All rooms should have a >60 min gap somewhere
    assert ("ECSS", "2.101") in buildings_rooms # Has 12:00 onwards gap
    assert ("ECSS", "2.102") in buildings_rooms # Has gaps before 10:00 and after 11:00
    assert ("JSOM", "1.101") in buildings_rooms # Is completely free

    # Find rooms in ECSS with at least 15 min gap
    free_rooms_ecss = test_db.get_rooms_with_sufficient_gap("ECSS", None, "2025-09-01", "08:00", "18:00", min_duration=15)
    buildings_rooms_ecss = {(r['building'], r['room']) for r in free_rooms_ecss}
    assert len(free_rooms_ecss) == 2
    assert ("ECSS", "2.101") in buildings_rooms_ecss # Has 10:30-11:00 gap
    assert ("ECSS", "2.102") in buildings_rooms_ecss # Has gaps

def test_get_rooms_with_sufficient_gap_not_found(test_db):
    """Test when no rooms meet the gap requirement"""
    # Add a blocking event to JSOM to make it busy
    test_db.add_event("JSOM", "1.101", "2025-09-03", "00:00", "23:59")
    
    free_rooms = test_db.get_rooms_with_sufficient_gap("JSOM", None, "2025-09-03", "08:00", "18:00", min_duration=1)
    assert len(free_rooms) == 0

def test_get_rooms_with_sufficient_gap_limit(test_db):
    """Test the limit parameter"""
    # All 3 rooms are available on this date
    free_rooms = test_db.get_rooms_with_sufficient_gap(None, None, "2025-10-01", "08:00", "18:00", min_duration=60, limit=2)
    assert len(free_rooms) == 2
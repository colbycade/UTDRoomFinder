from pymongo.mongo_client import MongoClient
import certifi
import os

SEMESTER_COLLECTION = "2025_Spring"
DATABASE_NAME = "database"

# Connection Functions
def get_mongo_client():
    # Store your MongoDB URI in an environment variable by running `export MONGODB_URI="your_mongodb_uri"` before running the app or script
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI environment variable is not set")
    
    # Initialize MongoDB client
    client = MongoClient(uri, tlsCAFile=certifi.where())
    return client

def get_db(database_name=DATABASE_NAME):
    client = get_mongo_client()
    db = client[database_name]
    return db

def get_collection(collection_name=SEMESTER_COLLECTION):
    db = get_db()
    collection = db[collection_name]
    return collection

def close_connection():
    client = get_mongo_client()
    client.close()

# Initialize the database connection
def initialize_db():
    global client, db, collection
    client = get_mongo_client()
    db = get_db()
    collection = get_collection()

# Utility Functions
def to_minutes(time_str):
    """Convert a time string (HH:MM) to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def parse_time_block(time_str):
    """Parse a time range string (e.g., "14:30 - 15:45") into start and end times."""
    try:
        start_time, end_time = time_str.split(" - ")
        return start_time, end_time
    except ValueError:
        print(f"Unexpected time range format: {time_str}")
        return None, None

# Database Operations
def get_room(building, room):
    """Return a specific room by building and room number."""
    return collection.find_one({"building": building, "room": room}, {"_id": 0}) # exclude id field

def get_buildings():
    """Return a sorted list of unique buildings."""
    buildings = collection.distinct("building")
    return sorted(buildings)

def get_rooms_by_building():
    """Return a dictionary mapping buildings to their room numbers."""
    pipeline = [
        {"$group": {"_id": "$building", "rooms": {"$push": "$room"}}}
    ]
    result = collection.aggregate(pipeline)
    building_to_rooms = {doc["_id"]: doc["rooms"] for doc in result}
    return building_to_rooms

def add_event(building, room, date, start_time, end_time, event_title="", notes="", status="User Reported"):
    """Add an event to the room's schedule for the specified date with validation."""
    # Validate start time is before end time
    start_minutes = to_minutes(start_time)
    end_minutes = to_minutes(end_time)
    if start_minutes >= end_minutes:
        return "Start time must be before end time"

    # Check for overlapping events
    if check_overlap(building, room, date, start_time, end_time):
        return "Event overlaps with an existing event"

    new_event = {
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "event_title": event_title,
        "notes": notes
    }

    # Add the event
    result = collection.update_one(
        {"building": building, "room": room},
        {"$push": {f"schedule.{date}": new_event}}
    )

    if result.matched_count == 0:
        # Room doesn't exist, create it
        collection.insert_one({
            "building": building,
            "room": room,
            "schedule": {date: [new_event]}
        })
    else:
        # Sort the schedule by start time just to keep it tidy
        room_data = get_room(building, room)
        if date in room_data['schedule']:
            sorted_events = sorted(room_data['schedule'][date], key=lambda x: x['start_time'])
            collection.update_one(
                {"building": building, "room": room},
                {"$set": {f"schedule.{date}": sorted_events}}
            )
    
    return True

def remove_user_event(building, room, date, time_block):
    """Remove a user-reported event from the room's schedule."""
    start_time, end_time = parse_time_block(time_block)
    if not start_time or not end_time:
        return False
    
    result = collection.update_one(
        {"building": building, "room": room},
        {"$pull": {f"schedule.{date}": {
            "start_time": start_time,
            "end_time": end_time,
            "status": "User Reported"
        }}}
    )
    
    return result.modified_count > 0

def cancel_event(building, room, date, time_block, notes=""):
    """Mark an event as cancelled in the room's schedule."""
    start_time, end_time = parse_time_block(time_block)
    if not start_time or not end_time:
        return False
    
    base_message = "User reported event as cancelled."
    cancellation_notes = base_message if not notes else f"{base_message} Explanation: {notes}"
    
    result = collection.update_one(
        {
            "building": building, 
            "room": room, 
            f"schedule.{date}": {
                "$elemMatch": {
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "Scheduled"
                }
            }
        },
        {"$set": {
            f"schedule.{date}.$.status": "Cancelled",
            f"schedule.{date}.$.notes": cancellation_notes
        }}
    )
    
    return result.modified_count > 0

def uncancel_event(building, room, date, time_block, notes=""):
    """Mark a cancelled event as scheduled again."""
    start_time, end_time = parse_time_block(time_block)
    if not start_time or not end_time:
        return False
    
    base_message = "User Confirmed."
    uncancel_notes = base_message if not notes else f"{base_message} Explanation: {notes}"
    
    result = collection.update_one(
        {
            "building": building, 
            "room": room, 
            f"schedule.{date}": {
                "$elemMatch": {
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "Cancelled"
                }
            }
        },
        {"$set": {
            f"schedule.{date}.$.status": "Scheduled",
            f"schedule.{date}.$.notes": uncancel_notes
        }}
    )
    
    return result.modified_count > 0

def check_overlap(building, room, date, start_time, end_time):
    """Check if the new event overlaps with any existing non-cancelled events."""
    room_data = get_room(building, room)
    if not room_data or date not in room_data.get('schedule', {}):
        return False  # No events, so no overlap

    start_minutes = to_minutes(start_time)
    end_minutes = to_minutes(end_time)

    for slot in room_data['schedule'].get(date, []):
        if slot['status'] == "Cancelled":
            continue  # Ignore cancelled events
        slot_start = to_minutes(slot['start_time'])
        slot_end = to_minutes(slot['end_time'])
        # Check for overlap
        if start_minutes < slot_end and end_minutes > slot_start:
            return True  # Overlap found
    return False  # No overlap

def find_available_slots(building, room, date, start_time="00:00", end_time="23:59"):
    """Find all available time slots for a room on a given date."""
    room_data = get_room(building, room)
    if not room_data or date not in room_data.get('schedule', {}) or not room_data['schedule'][date]:
        # If no events, the entire time range is available
        return [(start_time, end_time)]

    # Convert times to minutes for easier comparison
    start_minutes = to_minutes(start_time)
    end_minutes = to_minutes(end_time)

    # Get events for the day, excluding cancelled ones
    events = [slot for slot in room_data['schedule'][date] if slot['status'] != "Cancelled"]
    events.sort(key=lambda x: to_minutes(x['start_time']))

    available_slots = []
    current_time = start_minutes

    # Check gaps between events
    for event in events:
        event_start = to_minutes(event['start_time'])
        event_end = to_minutes(event['end_time'])

        # Skip events outside our time range
        if event_end <= start_minutes or event_start >= end_minutes:
            continue

        # If there's a gap before this event starts
        if current_time < event_start and event_start <= end_minutes:
            slot_start = max(current_time, start_minutes)
            slot_end = event_start
            if slot_start < slot_end:
                available_slots.append((
                    f"{slot_start // 60:02d}:{slot_start % 60:02d}",
                    f"{slot_end // 60:02d}:{slot_end % 60:02d}"
                ))

        # Move the current time to the end of this event
        current_time = max(current_time, event_end)

    # Check for a gap after the last event
    if current_time < end_minutes:
        available_slots.append((
            f"{current_time // 60:02d}:{current_time % 60:02d}",
            f"{end_minutes // 60:02d}:{end_minutes % 60:02d}"
        ))

    return available_slots

def get_next_availability_on_date(building, room, date, start_time="00:00", end_time="23:59", min_duration=1):
    """Find the next available time slot that meets the minimum duration."""
    available_slots = find_available_slots(building, room, date, start_time, end_time)
    min_duration = int(min_duration) if min_duration else 1

    # Find the first slot that meets the minimum duration
    for slot_start, slot_end in available_slots:
        slot_duration = to_minutes(slot_end) - to_minutes(slot_start)
        if slot_duration >= min_duration:
            return f"{slot_start} - {slot_end}"
    
    return None

def has_sufficient_gap(building, room, date, start_time, end_time, min_duration):
    """Check if a room has a gap of sufficient duration."""
    available_slots = find_available_slots(building, room, date, start_time, end_time)
    min_duration = int(min_duration) if min_duration else 1
    
    for slot_start, slot_end in available_slots:
        slot_duration = to_minutes(slot_end) - to_minutes(slot_start)
        if slot_duration >= min_duration:
            return True
    return False

def get_rooms_with_sufficient_gap(building, date, start_time, end_time, min_duration):
    """Return rooms with at least one gap of minimum duration."""
    
    # Default times if not provided
    start_time = start_time or "00:00"
    end_time = end_time or "23:59"
    min_duration = int(min_duration) if min_duration else 1
    
    query = {} if building == "Any Building" else {"building": building}
    rooms = list(collection.find(query, {"_id": 0}))
    
    free_rooms = []
    for room_data in rooms:
        # If no events on that day, the whole day is available
        if date not in room_data.get('schedule', {}) or not room_data['schedule'][date]:
            free_rooms.append(room_data)
            continue
        
        # Check for sufficient gaps
        if has_sufficient_gap(room_data['building'], room_data['room'], 
                             date, start_time, end_time, min_duration):
            free_rooms.append(room_data)
    
    return free_rooms
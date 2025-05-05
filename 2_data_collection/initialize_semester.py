# Written by Colby

from mongodb import get_db
from datetime import datetime, timedelta

'''
Each semester, we will scrape the course catalog for class information.
This data will be stored in the following schema:
- room_location (e.g., "SCI_1.159")
- monday_times (e.g., ["10:00-11:30"])
- tuesday_times
- wednesday_times
- thursday_times
- friday_times

The application needs to track each individual school day, so this script will 
take the scraped data and create a complete schedule for each room. 

New Schema:
- Room: Represents a room on campus
  - building (str): Building code (e.g., "ECSS")
  - room (str): Room number (e.g., "102")
  - schedule (dict): Mapping of dates to list of time blocks
    - Date (str): Format "YYYY-MM-DD" (e.g., "2025-03-24")
    - Time Block (dict): Represents a scheduled event
      - start_time (str): Start time in 24-hour format (e.g., "09:00")
      - end_time (str): End time in 24-hour format (e.g., "11:00")
      - status (str): "Scheduled", "Cancelled", or "User Reported"
      - event_title (str): Event name (e.g., "ENGL 1301")
      - notes (str): Additional notes about the event or cancellation

Steps: 
1. Create a new collection in the database for the semester
2. Manually set the semester start and end dates as well as holidays
3. For each class,
    - Initialize the room if it doesn't exist
    - Add all class times to that room's schedule
'''

# Adjust the following for the current semester (see https://www.utdallas.edu/academics/calendar/)
CLASS_INFO_COLLECTION = "class_information" # collection with scraped data
SEMESTER_COLLECTION = "2025_Spring" # name for the new collection
CLASSES_START = datetime(2025, 1, 21)
CLASSES_END = datetime(2025, 5, 9)
HOLIDAYS = [
    # Spring Break
    datetime(2025, 3, 17),
    datetime(2025, 3, 18),
    datetime(2025, 3, 19),
    datetime(2025, 3, 20),
    datetime(2025, 3, 21)
]

# Map weekdays to corresponding index for datetime weekday() function
WEEKDAY_KEYS = [
    ("monday_times", 0),
    ("tuesday_times", 1),
    ("wednesday_times", 2),
    ("thursday_times", 3),
    ("friday_times", 4)
]

# Get start and end time from a time range string (e.g., "14:30 - 15:45")
def parse_time_range(time_str):
    try:
        start_time, end_time = time_str.split(" - ")
        return start_time, end_time
    except ValueError:
        print(f"Unexpected time range format: {time_str}")
        return None, None
    
# Parse room location (e.g., "SCI_1.159") into building and room
def parse_room_location(room_location):
    try:
        building, room = room_location.split("_")
        return building, room
    except ValueError:
        print(f"Unexpected room location format: {room_location}")
        return None, None

# Get all days of a specific weekday in the semester
def get_weekday_dates(weekday_index):
    days = []
    for day_offset in range((CLASSES_END - CLASSES_START).days + 1):
        current_date = CLASSES_START + timedelta(days=day_offset)
        if current_date.weekday() == weekday_index and current_date not in HOLIDAYS:
            days.append(current_date)
    return days

# Transform and insert room data into the semester collection as events
def process_record(record, semester_collection):
    # Extract room and building
    if "room_location" not in record:
        print(f"No room_location field in record: {record.get('_id')}")
        return
    building, room = parse_room_location(record["room_location"])
    if not building or not room:
        return

    # Initialize room data if not exists
    room_schedule = {}
    
    # Iterate through each weekday
    for weekday_field, day_index in WEEKDAY_KEYS:
        time_strs = record.get(weekday_field, []) # array of time range strings
        if not time_strs:
            continue
        times = []
        for time_str in time_strs:
            start_time, end_time = parse_time_range(time_str)
            if start_time and end_time:
                times.append((start_time, end_time))

        # Iterate through all days in the semester of that weekday
        weekday_dates = get_weekday_dates(day_index)

        for curr_date in weekday_dates:
            date_str = curr_date.strftime("%Y-%m-%d")
            if date_str not in room_schedule:
                room_schedule[date_str] = []
            for start_time, end_time in times:
                event = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "status": "Scheduled", # all classes are initially marked as scheduled
                    "event_title": record.get("event_title", ""),
                    "notes": ""
                }
                room_schedule[date_str].append(event)
    
    # Update the room's schedule in the database
    try:
        semester_collection.update_one(
                {"building": building, "room": room},
                {"$set": {"schedule": room_schedule}},
                upsert=True  # create room if doesn't exist
            )
    except Exception as e:
        print(f"Error updating room {building}.{room}: {str(e)}")

def create_semester_schedule(class_info_collection, semester_collection):
    total_records = class_info_collection.count_documents({})
    print(f"Processing {total_records} class records")
    
    processed = 0
    next_milestone = 10 
    for record in class_info_collection.find():
        process_record(record, semester_collection)
        processed += 1

        # Log progress
        progress_percent = (processed / total_records) * 100
        if progress_percent >= next_milestone and progress_percent < 100:
            print(f"Processed {processed}/{total_records} records ({progress_percent:.1f}%)")
            next_milestone += 10
    print(f"Completed processing {processed} records")

if __name__ == "__main__":
    db = get_db()
    class_info_collection = db[CLASS_INFO_COLLECTION]
    semester_collection = db[SEMESTER_COLLECTION]

    # Clear existing data if rerunning
    semester_collection.drop()  # Clear existing data
    
    # Transform and insert data
    create_semester_schedule(class_info_collection, semester_collection)
    
    # Index for faster queries
    semester_collection.create_index([("building", 1), ("room", 1)]) 

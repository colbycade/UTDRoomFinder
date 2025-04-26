import os
import pandas as pd
import certifi
from pymongo import MongoClient, UpdateOne
from  room_schedule import Schedule
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# converts the spreadsheet of class information into a dictionary
# where the key is the room location and the value is the weekly 
# schedule of that room
def read_spreadsheet(filepath):
    rooms = {}
    day_index = { "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5 } 
   
    excel_data = pd.read_excel(filepath, header=2)
    for index, class_info in excel_data.iterrows():
        location = class_info.get('location')
        times = class_info.get('times')
        days = class_info.get('days')
        class_type = class_info.get('activity_type')
        
        if location == "ONLINE" or pd.isna(location) or pd.isna(times):    
            continue
        
        # create new entry into dictionary for new rooms
        if location not in rooms:
            rooms[location] = Schedule()

        if isinstance(days, str):
            for day in days.split(", "):
                if day in day_index:
                    rooms[location].add_class_time(day_index[day], times)

    return rooms

user = os.environ.get("mongodb_user")
password = os.environ.get("mongodb_pwd")
connection_string = f"mongodb+srv://{user}:{password}@classroominformation.kbuk2.mongodb.net/?appName=ClassroomInformation"
client = MongoClient(connection_string, tlsCAFile=certifi.where())

# ptr to classroom information folder in database directory
class_information_collection = client.database.test

# Check if the collection already exists and if so ask for confirmation to overwrite
collection_exists = class_information_collection.count_documents({}) > 0

# Ask for confirmation only once if collection exists
proceed_with_update = True
if collection_exists:
    confirm = input(f"Collection 'class_information' already exists in database. Proceed with updates? (y/n): ").lower()
    proceed_with_update = confirm == 'y' or confirm == 'yes'
if not proceed_with_update:
    print("Exiting without making any changes.")
    exit()

# possible fields of document to be send into database
fields = ["monday_times", "tuesday_times", "wednesday_times", "thursday_times", "friday_times", "saturday_times"]

# path to excel spreadsheets
downloads_path = "raw_classroom_information"

# dictionary that maps a rooms location to its weekly schedule
room_information = {}

for file_name in os.listdir(downloads_path):
   if file_name.endswith("xlsx"):
       room_information = read_spreadsheet(os.path.join(downloads_path, file_name))
       bulk_operations = []

       for room_location, room_schedule in room_information.items():
           set_data = {}

           for i, field in enumerate(fields):
               if room_schedule.days[i].times:
                   set_data[field] = room_schedule.days[i].times

           if set_data:
               bulk_operations.append(
                   UpdateOne(
                       {"room_location": room_location},
                       {"$set": set_data},
                       upsert=True
                   )
               )

       if bulk_operations:
           class_information_collection.bulk_write(bulk_operations)

       room_information = {}
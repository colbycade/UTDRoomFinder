import os
import pandas as pd
from pymongo import MongoClient
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
        
        if location == "ONLINE" or class_type != "Lecture":    
            continue

        elif pd.isna(location) or pd.isna(times):
            continue
        
        # create new entry into dictionary for new rooms
        if location not in rooms:
            rooms[location] = Schedule()

        if isinstance(days, str):
            for day in days.split(", "):
                if day in day_index:
                    rooms[location].add_class_time(day_index[day], times)

    return rooms

password = os.environ.get("mongodb_pwd")
connection_string = ""
client = MongoClient(connection_string)

# ptr to classroom information folder in database directory
class_information_collection = client.database.class_information

# possible fields of document to be send into database
fields = ["monday_times", "tuesday_times", "wednesday_times", "thursday_times", "friday_times", "saturday_times"]

# dictionary that maps a rooms location to its weekly schedule
room_information = {}

downloads_path = "raw_classroom_information"
for file_name in os.listdir(downloads_path):
    if file_name.endswith("xlsx"):
        room_information = read_spreadsheet(os.path.join(downloads_path, file_name))
        files_read += 1

        # going through each room's schedule and adding class times into the database
        for room_location, room_schedule in room_information.items():

            # updating existing document in mongodb
            existing_document = class_information_collection.find_one({"room_location": room_location})
            if existing_document:
                update_data = {}

                # add old times with new times read from spreadsheet
                for i, field in enumerate(fields):
                    if room_schedule.days[i].times:
                        existing_times = existing_document.get(field, [])
                        update_data[field] = existing_times + room_schedule.days[i].times

                class_information_collection.update_one({"room_location": room_location}, {"$set": update_data})

            # uploading an entiirely new document
            else:
                new_document = { "room_location": room_location } # data to send to database

                # only add days with classes as parameters 
                for i, field in enumerate(fields):
                    if room_schedule.days[i].times:
                        new_document[field] = room_schedule.days[i].times

                class_information_collection.insert_one(new_document)
        
        room_information = {}
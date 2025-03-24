from flask import Flask, render_template, request, jsonify
from mock_db import get_all_rooms, get_room, get_buildings, get_rooms_by_building, add_event, remove_user_event
from datetime import datetime

app = Flask(__name__)

# Home page with search form
@app.route('/')
def search():
    today = datetime.now().strftime('%Y-%m-%d')
    buildings = get_buildings()
    building_to_rooms = get_rooms_by_building()
    return render_template('search.html', today=today, buildings=buildings, building_to_rooms=building_to_rooms)

# Search results page
@app.route('/results', methods=['POST'])
def search_results():
    building = request.form.get('building')
    room = request.form.get('room')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    # Store search criteria for display
    criteria = {
        "building": building if building != "Any Building" else "Any Building",
        "room": room if room != "Any Room Number" else "Any Room Number",
        "date": date if date else "Any Date",
        "start_time": start_time if start_time else "Any Start Time",
        "end_time": end_time if end_time else "Any End Time"
    }

    # Convert times to 24-hour format for comparison
    def to_24hour(time_str):
        if not time_str:
            return None
        try:
            if 'AM' in time_str or 'PM' in time_str:
                return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M')
            if ':' in time_str:  # Simple HH:MM format check
                return time_str
            return None
        except ValueError:
            return None

    start_time_24 = to_24hour(start_time) if start_time else None
    end_time_24 = to_24hour(end_time) if end_time else None

    # Find available time slots for the results page
    results = []
    for room_data in get_all_rooms():
        # Filter by building if specified
        if building and building != 'Any Building' and room_data['building'] != building:
            continue
            
        # Filter by room if specified
        if room and room != 'Any Room Number' and room_data['room'] != room:
            continue

        # If no date is specified, check all dates in the schedule
        dates_to_check = [date] if date else room_data['schedule'].keys()
        available_slots = []

        for check_date in dates_to_check:
            if check_date not in room_data['schedule']:
                continue

            schedule = room_data['schedule'][check_date]
            
            # Case 1: No bookings means available all day
            if not schedule:
                default_start = "07:00"
                default_end = "22:00"
                
                # Apply time filters if specified
                if (not start_time_24 or start_time_24 <= default_end) and \
                   (not end_time_24 or end_time_24 >= default_start):
                    display_start = datetime.strptime(default_start, '%H:%M').strftime('%I:%M %p')
                    display_end = datetime.strptime(default_end, '%H:%M').strftime('%I:%M %p')
                    available_slots.append({
                        "building": room_data['building'],
                        "floor": room_data['floor'],
                        "room": room_data['room'],
                        "available_start": display_start,
                        "available_until": display_end
                    })
                continue
                
            # Case 2: Room has a schedule - find available blocks
            availability_blocks = []
            default_start = "07:00"
            default_end = "22:00"
            
            # Sort schedule by start time
            sorted_schedule = sorted(schedule, key=lambda x: x['start_time'])
            
            # Initialize with start of day if needed
            if sorted_schedule and sorted_schedule[0]['start_time'] > default_start:
                if sorted_schedule[0]['status'] != "Available":
                    availability_blocks.append({
                        "start": default_start,
                        "end": sorted_schedule[0]['start_time']
                    })
            
            # Find gaps between scheduled events
            for i in range(len(sorted_schedule)):
                current = sorted_schedule[i]
                
                # Add available blocks
                if current['status'] == "Available":
                    availability_blocks.append({
                        "start": current['start_time'],
                        "end": current['end_time']
                    })
                
                # Check for gap after current block
                if i < len(sorted_schedule) - 1:
                    next_block = sorted_schedule[i + 1]
                    if current['end_time'] < next_block['start_time'] and next_block['status'] != "Available":
                        availability_blocks.append({
                            "start": current['end_time'],
                            "end": next_block['start_time']
                        })
            
            # Add end of day if needed
            if sorted_schedule and sorted_schedule[-1]['end_time'] < default_end:
                if sorted_schedule[-1]['status'] != "Available":
                    availability_blocks.append({
                        "start": sorted_schedule[-1]['end_time'],
                        "end": default_end
                    })
            
            # If no schedule at all, room is available all day
            if not sorted_schedule:
                availability_blocks.append({
                    "start": default_start,
                    "end": default_end
                })
            
            # Filter blocks based on requested time
            for block in availability_blocks:
                # Skip if block doesn't meet time criteria
                if start_time_24 and block['end'] <= start_time_24:
                    continue
                if end_time_24 and block['start'] >= end_time_24:
                    continue
                
                # Convert to 12-hour format for display
                display_start = datetime.strptime(block['start'], '%H:%M').strftime('%I:%M %p')
                display_end = datetime.strptime(block['end'], '%H:%M').strftime('%I:%M %p')
                
                available_slots.append({
                    "building": room_data['building'],
                    "floor": room_data['floor'],
                    "room": room_data['room'],
                    "available_start": display_start,
                    "available_until": display_end
                })

        # If the room has any availability, add its first available slot to the results
        if available_slots:
            results.extend(available_slots[:1])  # Add only the first available slot for simplicity

    return render_template('results.html', rooms=results, criteria=criteria)

# Room schedule (API call)
@app.route('/api/schedule/<building>/<floor>/<room>')
def get_schedule(building, floor, room):
    room_data = get_room(building, floor, room)
    if room_data:
        return jsonify(room_data['schedule'])
    return jsonify({"error": "Room not found"}), 404

# Schedule page
@app.route('/schedule/<building>/<floor>/<room>')
def schedule(building, floor, room):
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('schedule.html', building=building, floor=floor, room=room, today=today)

# Report error (API call)
@app.route('/api/report', methods=['POST'])
def report_error():
    room = request.form.get('room')
    building = request.form.get('building')
    floor = request.form.get('floor')
    time_block = request.form.get('time_block')
    report_type = request.form.get('report_type')
    event_title = request.form.get('event_title', '')
    explanation = request.form.get('explanation', '')
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))  # Use current date if not provided

    if report_type == "add":
        # Parse the time block (e.g., "07:30 - 08:30")
        try:
            start_time, end_time = time_block.split(' - ')
        except ValueError:
            return jsonify({"error": "Invalid time block format"}), 400
        # Add the event using the abstracted function
        success = add_event(building, floor, room, date, start_time, end_time, event_title)
        if not success:
            return jsonify({"error": "Room not found"}), 404
        return jsonify({"status": "Event added", "building": building, "floor": floor, "room": room, "time_block": time_block, "event_title": event_title})

    elif report_type == "remove":
        # Remove the user-created event using the abstracted function
        success = remove_user_event(building, floor, room, date, time_block)
        if not success:
            return jsonify({"error": "Room or event not found"}), 404
        return jsonify({"status": "Event removed", "building": building, "floor": floor, "room": room, "time_block": time_block})

    elif report_type == "cancelled":
        return jsonify({"status": "Event marked as cancelled", "building": building, "floor": floor, "room": room, "time_block": time_block, "explanation": explanation})
    elif report_type == "verify":
        return jsonify({"status": "Event accuracy reported", "building": building, "floor": floor, "room": room, "time_block": time_block})
    elif report_type == "confirm":
        return jsonify({"status": "Event confirmed", "building": building, "floor": floor, "room": room, "time_block": time_block})

    return jsonify({"status": "Report submitted", "building": building, "floor": floor, "room": room, "time_block": time_block})

if __name__ == '__main__':
    app.run(debug=True)
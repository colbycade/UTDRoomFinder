# Utility Functions
from datetime import time

def to_minutes(time_str):
    """Convert a time string (HH:MM) to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def to_time_str(minutes):
    """Convert minutes since midnight to a time string (HH:MM)."""
    hours = minutes // 60
    minutes = minutes % 60
    return time(hours, minutes).strftime("%H:%M")
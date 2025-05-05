# Written by Colby

from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def initialize_db(self):
        """Initialize the database connection."""
        pass

    @abstractmethod
    def get_room(self, room, building):
        """Return a specific room by building and room number."""
        pass

    @abstractmethod
    def get_buildings(self):
        """Return a sorted list of unique buildings."""
        pass

    @abstractmethod
    def get_rooms_by_building(self, building):
        """Return a dictionary mapping buildings to their room numbers."""
        pass

    @abstractmethod
    def add_event(self, building, room, date, start_time, end_time, event_title, notes, status):
        """Add an event to the room's schedule for the specified date."""
        pass

    @abstractmethod
    def remove_user_event(self, room, building, date, start_time):
        """Remove a user-reported event from the room's schedule."""
        pass

    @abstractmethod
    def cancel_event(self, room, building, date, start_time):
        """Mark an event as cancelled in the room's schedule."""
        pass

    @abstractmethod
    def uncancel_event(self, room, building, date, start_time):
        """Mark a cancelled event as scheduled again."""
        pass

    @abstractmethod
    def get_rooms_with_sufficient_gap(self, building, room, date, duration, limit):
        """Return rooms with at least one gap of minimum duration."""
        pass

    @abstractmethod
    def get_next_availability_on_date(self, room, building, date, duration):
        """Find the next available time slot that meets the minimum duration."""
        pass
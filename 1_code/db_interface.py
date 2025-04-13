from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def initialize_db(self):
        pass

    @abstractmethod
    def get_room(self, room, building):
        pass

    @abstractmethod
    def get_buildings(self):
        pass

    @abstractmethod
    def get_rooms_by_building(self, building):
        pass

    @abstractmethod
    def add_event(self, room, building, date, event):
        pass

    @abstractmethod
    def remove_user_event(self, room, building, date, start_time):
        pass

    @abstractmethod
    def cancel_event(self, room, building, date, start_time):
        pass

    @abstractmethod
    def uncancel_event(self, room, building, date, start_time):
        pass

    @abstractmethod
    def get_rooms_with_sufficient_gap(self, building, date, duration):
        pass

    @abstractmethod
    def get_next_availability_on_date(self, room, building, date, duration):
        pass
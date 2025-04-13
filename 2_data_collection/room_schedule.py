class Day:
    def __init__(self):
        self.times = []

    def add_class_time(self, class_time: str):
        self.times.append(class_time)

class Schedule:
    def __init__(self):
        self.days = [Day() for _ in range(6)] # mon = 0, sat = 5

    def add_class_time(self, day: int, class_time: str):
        self.days[day].add_class_time(class_time)
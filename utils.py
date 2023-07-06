from datetime import datetime
from database.Attendance import Attendance


def get_time(attendance: Attendance):
    return attendance.date.time()


def get_time_str(attendance: Attendance):
    return attendance.date.strftime("%H:%M:%S:%f")

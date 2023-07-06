import sqlite3
from datetime import datetime, time
from typing import List, Type, Union

from database.Employee import Employee, EmployeeDatabase
from database.Attendance import Attendance, AttendanceDatabase


class Databases:
    def __init__(self):
        self.database = "presensi.db"
        self.Employee = EmployeeDatabase(db_file=self.database)
        self.Employee.create_table()
        self.Attendance = AttendanceDatabase(db_file=self.database)

    def get_all_employess(self, names: None = None):
        if names is None:
            return self.Employee.get_all_employees()
        else:
            return self.Employee.get_employees(names=names)

    def check_existing_employee_name(self, name: str) -> bool:
        return self.Employee.check_existing_employee_name(name=name)

    def add_attendance(self, attendance: Attendance):
        try:
            self.Attendance.add_attendance(attendance=attendance)
        except:
            return False
        return True


if __name__ == "__main__":
    db = Databases()
    emp = Employee(name="yusuf")
    att = Attendance(employee=emp, date=datetime.now())
    db.Attendance.add_attendance(attendance=att)

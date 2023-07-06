from datetime import datetime, time
import sqlite3

from .Employee import Employee, EmployeeDatabase


class Attendance:
    def __init__(
        self,
        id: int = None,
        employee: Employee = None,
        date: datetime = None,
        time: time = None,
    ) -> None:
        self.id = id
        self.employee = employee
        self.date = date
        self.time = time


class AttendanceDatabase:
    def __init__(self, db_file: str) -> None:
        self.db_file = db_file
        self._conn = None
        self.create_table()
        self._employee_db = EmployeeDatabase(self.db_file)

    def connect_db(self):
        self._conn = sqlite3.connect(
            self.db_file,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        return self._conn.cursor()

    def commit_db(self):
        self._conn.commit()
        self._conn.close()

    def create_table(self):
        c = self.connect_db()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     employeeID integer NOT NULL,
                     date timestamp NOT NULL)
            """
        )

        self.commit_db()

    def add_attendance(self, attendance: Attendance):
        c = self.connect_db()

        emp_id = attendance.employee.id
        if emp_id is None:
            if attendance.employee.name is None:
                raise ValueError("Employee name not provided.")

            emps = self._employee_db.get_employee(
                name=[
                    attendance.employee.name,
                ]
            )
            if len(emps) > 0:
                emp_id = emps[0].id
            else:
                raise Exception("Name not exists in database.")

        date = attendance.date

        c.execute(
            """
            INSERT INTO attendance (employeeID, date)
                VALUES (?, ?)
            """,
            (emp_id, date),
        )

        self.commit_db()

    def get_all_attendance(self):
        pass


if __name__ == "__main__":
    emp = Employee(name="yusuf")
    att = Attendance(employee=emp, date=datetime.now())
    db = AttendanceDatabase("presensi.db")
    db.add_attendance(attendance=att)

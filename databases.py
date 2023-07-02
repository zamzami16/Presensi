import sqlite3
from datetime import datetime


import sqlite3


class Employee:
    def __init__(self, id, name, address, faces):
        self.id = id
        self.name = name
        self.address = address
        self.faces = faces


class EmployeeDatabase:
    def __init__(self, db_file):
        self.db_file = db_file

    def create_table(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS employees
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     address TEXT,
                     faces BLOB)
            """
        )

        conn.commit()
        conn.close()

    def add_employee(self, employee):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO employees (name, address, faces)
                    VALUES (?, ?, ?)
            """,
            (employee.name, employee.address, employee.faces),
        )

        conn.commit()
        conn.close()

    def get_all_employees(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("SELECT * FROM employees")
        rows = c.fetchall()

        employees = []
        for row in rows:
            id, name, address, faces = row
            employee = Employee(id, name, address, faces)
            employees.append(employee)

        conn.close()

        return employees

    def delete_employee(self, employee_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        c.execute("DELETE FROM employees WHERE id=?", (employee_id,))

        conn.commit()
        conn.close()

    def check_existing_employee_name(self, name: str) -> bool:
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM employees WHERE name=?", (name,))
        rows = c.fetchone()
        if rows is not None:
            return True
        return False


class Databases:
    def __init__(self):
        self.database = "presensi.db"
        self.Employee = EmployeeDatabase(self.database)
        self.Employee.create_table()

    def get_all_employess(self):
        return self.Employee.get_all_employees()

    def check_existing_employee_name(self, name: str) -> bool:
        return self.Employee.check_existing_employee_name(name=name)

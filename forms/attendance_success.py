import sys
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QSpacerItem,
    QLabel,
    QWidget,
    QSizePolicy,
    QDateTimeEdit,
)

# from databases import Employee, Databases
from database.Attendance import Attendance


class EmployeeAttendance(QDialog):
    def __init__(self, parent: None, attendance: Attendance, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setWindowTitle("Attendance")
        self.setMinimumSize(200, 100)

        # check name and date in the kwargs
        if attendance is None:
            raise ValueError("Attendance oject not supplied.")

        self.attendance = attendance
        self.attendance.time = self.attendance.date.time()

        # Set up dialog layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        self.main_layout.addWidget(form_widget)

        self.line_edit = QLineEdit()
        self.date_time_edit = QDateTimeEdit()

        # Set initial values and properties
        self.line_edit.setText(attendance.employee.name)
        self.date_time_edit.setDateTime(attendance.date)
        self.line_edit.setReadOnly(True)
        self.date_time_edit.setReadOnly(True)

        form_layout.addRow("Name:", self.line_edit)
        form_layout.addRow("Date:", self.date_time_edit)

        # Add buttons
        button_layout = QHBoxLayout()
        self.main_layout.addLayout(button_layout)

        spacer_item = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        button_layout.addSpacerItem(spacer_item)

        ok_button = QPushButton("OK")
        ok_button.setFixedSize(80, 30)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(80, 30)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # create layout


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = EmployeeAttendance(parent=None, **{"name": "yusuf"})
    dialog.exec_()

    sys.exit(app.exec_())

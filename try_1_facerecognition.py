import cv2
import face_recognition
import numpy as np
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QMessageBox,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime

from forms.register_employees import (
    EmployeeRegistration,
)

from databases import Employee, Databases


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Attendance System.")
        self.setMinimumSize(800, 600)
        self.running = False

        # add field for counting smile face
        self._prev_faces = ""
        self._smiling = []

        # initialize the database
        self.database = Databases()

        # initialize data
        self.known_encodings = []
        self.known_names = []
        self.fetch_known_faces_from_database()

        # Create a label to display the video feed
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        # Create start and stop buttons
        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setEnabled(False)  # Disable the stop button initially

        # Create an attendance label
        self.attendance_label = QLabel(self)
        self.attendance_label.setFixedHeight(30)
        self.attendance_label.setAlignment(Qt.AlignCenter)
        self.attendance_label.setText("Attendance:")

        # Create a register employee button
        self.register_button = QPushButton("Register Employee", self)

        # Create a layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.attendance_label)
        layout.addWidget(self.register_button)

        # Create a central widget and set the layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set up event handlers for buttons
        self.start_button.clicked.connect(self.start_video_capture)
        self.stop_button.clicked.connect(self.stop_video_capture)
        self.register_button.clicked.connect(self.open_registration_dialog)

        # Haar cascade model
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )

        # Initialize OpenCV capture object
        self.capture = cv2.VideoCapture(0)
        self.attendance = {}

    def start_video_capture(self):
        self.stop_button.setEnabled(True)
        self.start_button.setEnabled(False)
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def stop_video_capture(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.capture is not None:
            self.capture.release()

    def update_frame(self):
        # cek for 10 smiling frame
        if self._smiling.count(True) > 10:
            QMessageBox.information(
                self, "attendance", "You are logged in to attendance."
            )
            self.attendance_label.setText(
                f"Attendance: {self._prev_faces} on {datetime.now()}."
            )
            self._prev_faces = ""
            self._smiling = []
            self.stop_video_capture()

        ret, frame = self.capture.read()
        if ret:
            # Perform face detection
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(
                frame, face_locations
            )

            for face_encoding in face_encodings:
                # Compare the face encoding with known encodings
                known_encodings = (
                    self.known_encodings
                )  # List of known face encodings
                known_names = (
                    self.known_names
                )  # List of corresponding employee names

                matches = face_recognition.compare_faces(
                    known_encodings, face_encoding
                )
                name = "Unknown"

                if np.any(matches):
                    matched_indices = np.where(matches)[0]
                    name = known_names[matched_indices[0]]

                # Draw a rectangle around the detected face and display the employee's name
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(
                    frame, (left, top), (right, bottom), (0, 255, 0), 2
                )
                cv2.putText(
                    frame,
                    name,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2,
                )

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                for top, right, bottom, left in face_locations:
                    # Extract the region of interest (ROI) corresponding to the face
                    face_roi_gray = gray[top:bottom, left:right]
                    face_roi_color = frame[top:bottom, left:right]

                    # Perform smile detection on the face ROI
                    smiles = self.smile_cascade.detectMultiScale(
                        face_roi_gray, scaleFactor=1.7, minNeighbors=11
                    )

                    if len(smiles) > 0:
                        if self._prev_faces == name:
                            self._smiling.append(True)
                        else:
                            self._smiling = []
                            self._prev_faces = name
                    else:
                        self._smiling.append(False)

                    # Draw smile boxes on the face ROI
                    for sx, sy, sw, sh in smiles:
                        cv2.rectangle(
                            face_roi_color,
                            (sx, sy),
                            (sx + sw, sy + sh),
                            (255, 0, 0),
                            2,
                        )

            # Convert the frame to QImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(
                frame.data,
                frame.shape[1],
                frame.shape[0],
                QImage.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio)

            # Set the pixmap in the video label
            self.video_label.setPixmap(pixmap)
            self.video_label.update()

    def closeEvent(self, event):
        # Release the camera when the application is closed
        self.running = False
        if self.capture is not None:
            self.capture.release()
        event.accept()

    def open_registration_dialog(self):
        dialog = EmployeeRegistration(self)
        if dialog.exec_() == QDialog.Accepted:
            # Registration successful, perform necessary actions if needed
            pass

    def fetch_known_faces_from_database(self):
        employees = self.database.get_all_employess()

        for employee in employees:
            # Convert the face image data to numpy array
            face_image = cv2.imdecode(
                np.frombuffer(employee.faces, np.uint8), cv2.IMREAD_UNCHANGED
            )

            # Perform face detection
            face_encoding = face_recognition.face_encodings(face_image)
            if len(face_encoding) > 0:
                # Append the face encoding and corresponding name to the lists
                self.known_encodings.append(face_encoding)
                self.known_names.append(employee.name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

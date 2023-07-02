import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

# Constants for face and smile detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

# Employee attendance system class
class EmployeeAttendanceSystem(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize variables
        self.employee_models = []  # List to store employee models
        self.current_employee = None  # Variable to store the current employee

        # Create GUI elements
        self.label = QLabel(self)
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_attendance_system)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        self.setLayout(layout)

        # Set up the timer for video capture
        self.timer = QTimer()
        self.timer.timeout.connect(self.detect_faces)

    def start_attendance_system(self):
        self.timer.start(3)  # Start the timer with 30ms interval

    def detect_faces(self):
        # Capture video from the default camera
        video_capture = cv2.VideoCapture(0)

        # Read the current frame
        ret, frame = video_capture.read()

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        # Process each detected face
        for (x, y, w, h) in faces:
            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Extract the face ROI
            face_roi_gray = gray[y:y+h, x:x+w]
            face_roi_color = frame[y:y+h, x:x+w]

            # Detect smiles within the face ROI
            smiles = smile_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.5, minNeighbors=15)

            # Process each detected smile
            for (sx, sy, sw, sh) in smiles:
                # Draw a rectangle around the smile
                cv2.rectangle(face_roi_color, (sx, sy), (sx+sw, sy+sh), (255, 0, 0), 2)

                # Check if the smile belongs to a known employee
                if self.current_employee:
                    # Record the attendance for the current employee
                    print(f"Attendance recorded for employee: {self.current_employee}")

        # Convert the frame to RGB format for display in PyQt
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape

        # Create a QImage from the RGB image data
        qt_image = QImage(rgb_image.data, w, h, w * ch, QImage.Format_RGB888)

        # Create a QPixmap and set it as the label's pixmap
        pixmap = QPixmap.fromImage(qt_image)
        self.label.setPixmap(pixmap)

        # Release the video capture object
        video_capture.release()

    def add_employee(self, employee_name):
        # Add employee to the employee models list
        self.employee_models.append(employee_name)

    def build_models(self):
        # Build employee models using the captured training data
        pass  # Add your implementation here


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create an instance of the employee attendance system
    attendance_system = EmployeeAttendanceSystem()
    attendance_system.show()

    # Add employees to the system (you can modify or extend this as needed)
    attendance_system.add_employee("John Doe")
    attendance_system.add_employee("Jane Smith")

    # Build employee models
    attendance_system.build_models()

    sys.exit(app.exec_())

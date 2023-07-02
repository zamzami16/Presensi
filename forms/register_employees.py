import cv2
import time
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLabel,
)

from databases import Employee, Databases


class EmployeeRegistration(QDialog):
    def __init__(self, parent: None):
        super().__init__(parent)
        self.setWindowTitle("Register Employee")
        self.face_captured = False
        self.smiling = False

        # Haar cascade model
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )

        # Create form layout for employee information
        self.form_layout = QFormLayout()

        # Create line edits for employee information
        self.name_edit = QLineEdit()
        self.address_edit = QLineEdit()

        # Add line edits to the form layout
        self.form_layout.addRow("Name:", self.name_edit)
        self.form_layout.addRow("Address:", self.address_edit)

        # Create capture button
        self.capture_button = QPushButton("Capture")
        self.capture_button.clicked.connect(self.capture_face)

        # Create retake button
        self.retake_button = QPushButton("Retake")
        self.retake_button.clicked.connect(self.retake_capture)
        self.retake_button.setEnabled(False)

        # Create register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_employee)
        self.register_button.setEnabled(False)

        # Create captured image label
        self.captured_image_label = QLabel(self)
        self.captured_image_label.setFixedSize(QSize(400, 400))
        self.captured_image_label.setAlignment(Qt.AlignCenter)

        # Create layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(self.captured_image_label)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.retake_button)
        layout.addLayout(self.form_layout)
        layout.addWidget(self.register_button)
        self.setLayout(layout)

        # Initialize the capture flag and captured image
        self.capture_flag = True
        self.captured_image = None

    def showEvent(self, event):
        super().showEvent(event)
        self.start_video_capture()

    def capture_face(self):
        if self.capture is None or not self.capture.isOpened():
            self.start_video_capture()

        if self.smiling:
            self.face_captured = True
            self.capture_flag = False
            self.retake_button.setEnabled(True)
            self.register_button.setEnabled(True)
            self.capture_button.setEnabled(False)
            self.stop_video_capture()

    def retake_capture(self):
        self.captured_image_label.clear()
        self.capture_button.setText("Capture")
        self.capture_flag = True
        self.retake_button.setEnabled(False)
        self.capture_button.setEnabled(True)
        self.register_button.setEnabled(False)

        # Restart the video capture
        self.start_video_capture()

    def start_video_capture(self):
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def stop_video_capture(self):
        if self.capture is not None:
            self.capture.release()

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            # Convert the frame to QImage
            frame2save = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform face detection
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            # Draw rectangles around the detected faces
            for x, y, w, h in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                roi_gray = gray[y : y + h, x : x + w]
                roi_color = frame[y : y + h, x : x + w]

                # Perform smile detection
                smiles = self.smile_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.7,
                    minNeighbors=22,
                    minSize=(25, 25),
                )
                if len(smiles) > 0:
                    self.smiling = True
                else:
                    self.smiling = False

                # Draw rectangles around the detected smiles
                for sx, sy, sw, sh in smiles:
                    cv2.rectangle(
                        roi_color,
                        (sx, sy),
                        (sx + sw, sy + sh),
                        (255, 0, 0),
                        2,
                    )

                # Store the captured image when a smile is detected
                if self.smiling:
                    # self.captured_image = frame[y : y + h, x : x + w].copy()
                    self.captured_image = frame2save

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(
                frame_rgb,
                frame_rgb.shape[1],
                frame_rgb.shape[0],
                QImage.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(
                self.captured_image_label.size(), Qt.KeepAspectRatio
            )
            self.captured_image_label.setPixmap(pixmap)
            self.captured_image_label.update()

    def register_employee(self):
        name = self.name_edit.text()
        address = self.address_edit.text()
        databases = Databases()

        if not self.smiling:
            QMessageBox.warning(
                self,
                "not smiling",
                "The captured image not smiling.",
            )
            return

        if name.strip() is None:
            QMessageBox.warning(
                self,
                "Name can't be null.",
                "The name will be username and can not be null or whitespace.",
            )
            return

        # Perform validation of employee information here if needed
        if databases.check_existing_employee_name(name=name):
            QMessageBox.warning(
                self,
                f"Name {name} Already Exists",
                f"The name {name} already exists in the database. Please choose a different name.",
            )
            return

        if self.face_captured:
            # Create a new employee object with the face image
            image_data = cv2.imencode(".png", self.captured_image)[1].tobytes()
            employee = Employee(
                id=None, name=name, address=address, faces=image_data
            )

            # Add the new employee to the database
            databases.Employee.add_employee(employee)

            QMessageBox.information(
                self,
                "success",
                "Data was saved to database.",
            )

            # Close the dialog
            self.accept()
        else:
            # Face not captured, display an error message or perform necessary validation
            QMessageBox.critical(
                self,
                f"Image not captured.",
                f"There are no image to saved into database. Please capture the image first!",
            )
            return

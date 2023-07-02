import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QSize
import cv2


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.running = False
        self.setFixedSize(QSize(800, 600))
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

        # Create a layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.attendance_label)

        # Create a central widget and set the layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set up event handlers for buttons
        self.start_button.clicked.connect(self.start_video_stream)
        self.stop_button.clicked.connect(self.stop_video_stream)

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

    def start_video_stream(self):
        # Enable the stop button and disable the start button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.running = True
        # Start the video stream
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                # Convert the frame to QImage
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

                    # Draw rectangles around the detected smiles
                    for sx, sy, sw, sh in smiles:
                        cv2.rectangle(
                            roi_color,
                            (sx, sy),
                            (sx + sw, sy + sh),
                            (255, 0, 0),
                            2,
                        )

                    # Update attendance record
                    employee_name = "John"  # Replace with actual employee name
                    if len(smiles) > 0:
                        self.attendance[employee_name] = "Present"
                    else:
                        self.attendance[employee_name] = "Absent"

                # Convert the frame to QImage
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(
                    frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888
                )
                pixmap = QPixmap.fromImage(image)
                pixmap = pixmap.scaled(
                    self.video_label.size(), Qt.KeepAspectRatio
                )

                # Set the pixmap in the video label
                self.video_label.setPixmap(pixmap)
                self.video_label.update()
                QApplication.processEvents()

    def stop_video_stream(self):
        # Disable the stop button and enable the start button
        self.running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Display attendance
        attendance_text = "Attendance:\n"
        for employee, status in self.attendance.items():
            attendance_text += f"{employee}: {status}\n"
        self.attendance_label.setText(attendance_text)

    def closeEvent(self, event):
        # Release the camera when the application is closed
        self.running = False
        if self.capture is not None:
            self.capture.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

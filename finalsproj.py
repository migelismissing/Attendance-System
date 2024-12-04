import cv2
import os
import numpy as np
import time
from managers import WindowManager, CaptureManager

class FaceRecognition:
    def __init__(self):
        # Initialize the window and capture manager
        self._WindowManager = WindowManager('Face Recognition')
        self._captureManager = CaptureManager(cv2.VideoCapture(0), self._WindowManager, False)
        self._face_cascade = cv2.CascadeClassifier('C:/Users/Ron Von Angeles/Downloads/haarcascade_frontalface_default.xml')
        self._recognizer = cv2.face.EigenFaceRecognizer_create()
        self._label_map = {}  # Map label numbers to names
        self._time_recog = {}  # Track recognition time for each person
        self._latest_face = None  # To track the last recognized person

    def faceRec(self):
        """Train the face recognizer on the dataset."""
        image_folder = 'C:/Users/Ron Von Angeles/OneDrive/Documents/pythonfoldere/Accounts/datasets'
        X, y = [], []
        current_label = 0

        for subdirname in os.listdir(image_folder):
            subject_path = os.path.join(image_folder, subdirname)
            if os.path.isdir(subject_path):
                self._label_map[current_label] = subdirname  # Map label to folder name
                for filename in os.listdir(subject_path):
                    try:
                        if filename.endswith('.pgm'):
                            filepath = os.path.join(subject_path, filename)
                            im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

                            # Resize image to 200x200
                            im = cv2.resize(im, (200, 200))

                            X.append(np.asarray(im, dtype=np.uint8))
                            y.append(current_label)

                    except IOError as e:
                        print(f"I/O Error({e.errno}): {e.strerror}")
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                current_label += 1  # Increment for the next person

        print(f"Label map: {self._label_map}")  # Debug
        X = np.asarray(X, dtype=np.uint8)
        y = np.asarray(y, dtype=np.int32)
        print(f"Training on {len(X)} images with labels: {y}")  # Debug
        self._recognizer.train(X, y)

    def detectFaces(self, frame):
        """Detect and recognize faces in the given frame."""
        names = list(self._label_map.values())  # List of names from the label map
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray_frame, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
            roi_gray = gray_frame[y:y + h, x:x + w]
            roi_resized = cv2.resize(roi_gray, (200, 200))

            # Recognize the face
            label, confidence = self._recognizer.predict(roi_resized)
            label_name = names[label] if label < len(names) else "Unknown"

            # If confidence is too low, mark as unknown
            if confidence > 10000:
                label_name = "Unknown"

            # Display name on the frame
            cv2.putText(frame, label_name, (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Reset timer if the recognized person changes_
            current_time = time.time()
            if label_name != "Unknown":
                if label_name != self._latest_face:
                    # New person recognized, reset the timer
                    self._latest_face = label_name
                    self._time_recog = {label_name: current_time}  
                else:
                    # Check if recognized for 5 seconds
                    elapsed_time = current_time - self._time_recog[label_name]
                    if elapsed_time >= 5:
                        cv2.putText(frame, f"{label_name} is present!", (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
            else:
                # Reset recognition timer if not recognized
                if label_name in self._time_recog:
                    del self._time_recog[label_name]

    def run(self):
        """Run the main loop."""
        self.faceRec()  # Train the recognizer
        self._WindowManager.createWindow()
        while self._WindowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame

            if frame is not None:
                self.detectFaces(frame)

            self._captureManager.exitFrame()
            self._WindowManager.processEvents()

if __name__ == "__main__":
    FaceRecognition().run()

import tkinter as tk
from tkinter import messagebox
from scipy.spatial import distance
from imutils import face_utils
from pygame import mixer
import imutils
import dlib
import cv2
import os

# Initialize mixer and load alert sound
mixer.init()
mixer.music.load("music.wav")

# Function to calculate Eye Aspect Ratio (EAR)
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Thresholds
thresh = 0.25
frame_check = 20

# Load Dlib's face detector and shape predictor
detect = dlib.get_frontal_face_detector()
predictor_path = "models/shape_predictor_68_face_landmarks.dat"
if not os.path.exists(predictor_path):
    raise FileNotFoundError(f"Shape predictor model not found at '{predictor_path}'")
predict = dlib.shape_predictor(predictor_path)

# Facial landmarks for the eyes
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]

# Drowsiness detection logic
def detect_drowsiness():
    global flag
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detect(gray, 0)

        for subject in subjects:
            shape = predict(gray, subject)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if ear < thresh:
                flag += 1
                if flag >= frame_check:
                    cv2.putText(frame, "****************ALERT!****************", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "****************ALERT!****************", (10, 325),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if not mixer.music.get_busy():  # Play only if not already playing
                        mixer.music.play()
            else:
                flag = 0
                mixer.music.stop()

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start button action
def start_detection():
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    detect_drowsiness()

# Stop button action
def stop_detection(cap=None):
    cap.release()
    cv2.destroyAllWindows()
    start_button.config(state="normal")
    stop_button.config(state="disabled")
    mixer.music.stop()

# Create the main window
window = tk.Tk()
window.title("Drowsiness Detection System")
window.geometry("400x300")
window.config(bg="#f5f5f5")

# Create a label
label = tk.Label(window, text="Drowsiness Detection System", font=("Arial", 16, "bold"), bg="#f5f5f5", fg="#333")
label.pack(pady=20)

# Create instruction label
instruction_label = tk.Label(window, text="Click 'Start Detection' to begin monitoring for drowsiness.",
                             font=("Arial", 12), bg="#f5f5f5", fg="#555")
instruction_label.pack(pady=10)

# Create start and stop buttons
button_frame = tk.Frame(window, bg="#f5f5f5")
start_button = tk.Button(button_frame, text="Start Detection", font=("Arial", 14), command=start_detection, bg="#4CAF50", fg="white", relief="raised")
stop_button = tk.Button(button_frame, text="Stop Detection", font=("Arial", 14), command=stop_detection, state="disabled", bg="#f44336", fg="white", relief="raised")

start_button.grid(row=0, column=0, padx=10, pady=10)
stop_button.grid(row=0, column=1, padx=10, pady=10)

button_frame.pack(pady=20)

# Start the Tkinter event loop
window.mainloop()

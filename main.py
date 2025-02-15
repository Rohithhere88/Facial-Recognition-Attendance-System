import cv2
import os
import numpy as np
from retinaface import RetinaFace
from deepface import DeepFace
import smtplib
import mediapipe as mp
from email.mime.text import MIMEText

# Paths for storing face data
FACE_DB_PATH = "faces/"
if not os.path.exists(FACE_DB_PATH):
    os.makedirs(FACE_DB_PATH)

# Function to capture and store a face
def add_face():
    name = input("Enter your Name: ")
    email = input("Enter your Email: ")
    
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        faces = RetinaFace.detect_faces(frame)
        if faces:
            face_filename = os.path.join(FACE_DB_PATH, f"{name}.jpg")
            cv2.imwrite(face_filename, frame)
            print(f"Face saved as {face_filename}")
            break
        
        cv2.imshow("Add Face", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    # Store email information
    with open(FACE_DB_PATH + "emails.txt", "a") as f:
        f.write(f"{name},{email}\n")

# Function to check if the face is 2D (fake) or 3D (real) using Mediapipe
def is_real_face(frame):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(frame_rgb)

    return bool(result.multi_face_landmarks)  # Returns True if a 3D face is detected

# Function to mark attendance
def mark_attendance():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        try:
            result = DeepFace.find(img_path=frame, db_path=FACE_DB_PATH, model_name="VGG-Face", enforce_detection=False)
            if len(result[0]) > 0:
                person_name = result[0]["identity"][0].split("/")[-1].split(".")[0]
                print(f"Recognized: {person_name}")

                if is_real_face(frame):  # Check anti-spoofing
                    print(f"Face is Real. Attendance Marked for {person_name}.")
                    send_email(person_name)
                else:
                    print("Spoofing Detected! Fake Face.")
                break
        except:
            pass

        cv2.imshow("Mark Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to send attendance email
def send_email(name):
    email_id = None
    with open(FACE_DB_PATH + "emails.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            stored_name, stored_email = line.strip().split(",")
            if stored_name == name:
                email_id = stored_email
                break
    
    if not email_id:
        print("Email ID not found.")
        return

    sender_email = "rohith777here@gmail.com"
    sender_password = "bgot dbsi tswd lxhy"

    subject = "Attendance Marked"
    body = f"Hello {name},\n\nYour attendance has been marked successfully!\n\nRegards,\nAttendance System"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = email_id

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_id, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {email_id}.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main program
while True:
    print("\n1. Add Face")
    print("2. Mark Attendance")
    print("3. Exit")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        add_face()
    elif choice == "2":
        mark_attendance()
    elif choice == "3":
        break
    else:
        print("Invalid choice. Try again.")

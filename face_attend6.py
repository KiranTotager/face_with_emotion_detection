import tkinter as tk
from tkinter import ttk
import cv2 as cv
import numpy as np
import datetime as dt
import mysql.connector
from mysql.connector import Error
from concurrent.futures import ThreadPoolExecutor
from deepface import DeepFace
import os
from PIL import Image, ImageTk
import time
import threading
import pandas as pd
from tensorflow.keras.models import load_model
import random
import hashlib
from ultralytics import YOLO
import os
import re
import tkinter.messagebox as MessageBox

# Initialize face cascade
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

emotion_model = load_model('models/emotion_model.h5')
age_net = cv.dnn.readNetFromCaffe('models/age_deploy.prototxt', 'models/age_net.caffemodel')
gender_net = cv.dnn.readNetFromCaffe('models/deploy.prototxt', 'models/gender_net.caffemodel')

# Labels for emotion, gender, age
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
gender_labels = ['Male', 'Female']
age_labels = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']

# Database setup
db_config = {
    'host': 'localhost',  # Replace with your MySQL server host
    'user': 'root',  # Your MySQL username
    'password': '',  # Your MySQL password (default is empty for XAMPP)
    'database': 'AttendanceSystem'  # Replace with your database name
}





def recognize_person(face_roi, db_path="FaceData", threshold=0.5, model_name="VGG-Face"):
    """
    Recognizes a person using DeepFace by comparing the face ROI with a database.
    Supports identifying both registered and unknown individuals.

    Parameters:
        face_roi: Image of the face region of interest.
        db_path: Path to the facial database directory.
        threshold: Distance threshold for recognizing a face.
        model_name: The DeepFace model to use for embedding generation and comparison.

    Returns:
        A dictionary with recognition results:
        - 'status': "Registered" or "Unknown"
        - 'name': Recognized person's name (if registered) or "Unknown"
        - 'distance': Similarity score (lower is more similar)
    """
    from deepface import DeepFace
    import os

    try:
        # Search for a match in the database
        results = DeepFace.find(face_roi, db_path=db_path, model_name=model_name, enforce_detection=False, silent=True)

        if len(results) > 0:
            # Extract the closest match and its similarity score
            closest_match = results[0].iloc[0]  # Take the top match
            similarity_score = closest_match["distance"]
            recognized_person = os.path.basename(os.path.dirname(closest_match["identity"]))

            if similarity_score < threshold:
                # Registered person recognized
                return {
                    "status": "Registered",
                    "name": recognized_person,
                    "distance": similarity_score,
                }
            else:
                # Face exists but doesn't meet the threshold
                return {
                    "status": "Unknown",
                    "name": "Unknown",
                    "distance": similarity_score,
                }
        else:
            # No match found in the database
            return {
                "status": "Unknown",
                "name": "Unknown",
                "distance": None,
            }

    except Exception as e:
        print(f"Error during recognition: {e}")
        return {
            "status": "Error",
            "name": "Unknown",
            "distance": None,
        }


def fetch_user_details(usn):
    """Fetch user details from the MySQL database."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    fetch_query = """
        SELECT name, branch, sem, dob FROM users WHERE usn = %s
    """
    cursor.execute(fetch_query, (usn,))
    user_details = cursor.fetchone()
    conn.close()

    if user_details:
        print(f"User Details: {user_details}")
    else:
        print(f"No user found with USN: {usn}")

    return user_details

def mark_attendance(usn):
    """Marks the attendance of a person by adding their details and timestamp to the database."""
    date_ = dt.date.today().strftime("%Y-%m-%d")
    time_ = dt.datetime.now().strftime("%H:%M:%S")
    table_name = f"attendance_{date_.replace('-', '_')}"

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()

            # Ensure the date-specific table exists with columns for first and most recent attendance times
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    usn VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    branch VARCHAR(255) NOT NULL,
                    sem VARCHAR(255) NOT NULL,
                    dob DATE NOT NULL,
                    erlier TIME,
                    recent TIME
                )
            """
            cursor.execute(create_table_query)
            print(f"Table {table_name} ensured to exist.")

            # Fetch user details from the `users` table
            cursor.execute("SELECT name, branch, semester, dob FROM users WHERE usn = %s", (usn,))
            user_details = cursor.fetchone()

            if not user_details:
                print(f"Error: No user found with USN {usn}.")
                return

            name, branch, sem, dob = user_details

            # Check if the user is already marked present for the day
            cursor.execute(f"SELECT * FROM {table_name} WHERE usn = %s", (usn,))
            record = cursor.fetchone()

            if not record:
                print("Marking first attendance")
                # Insert a new record with the first attendance time
                insert_query = f"""
                    INSERT INTO {table_name} (usn, name, branch, sem, dob, erlier, recent) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (usn, name, branch, sem, dob, time_, time_))
                connection.commit()
                print(f"First attendance marked for {name} ({usn}) at {time_}.")
            else:
                erlier = record[5]
                recent = record[6]

                if not erlier:
                    print("Marking first attendance")
                    # Update first attendance time if it's not set
                    update_query = f"""
                        UPDATE {table_name} SET erlier = %s 
                        WHERE usn = %s
                    """
                    cursor.execute(update_query, (time_, usn))
                    connection.commit()
                    print(f"First attendance marked for {name} ({usn}) at {time_}.")

                # Always update most recent attendance time
                update_recent_query = f"""
                    UPDATE {table_name} SET recent = %s 
                    WHERE usn = %s
                """
                cursor.execute(update_recent_query, (time_, usn))
                connection.commit()
                print(f"Most recent attendance updated for {name} ({usn}) at {time_}.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# def process_frame(frame, db_path="FaceData", frame_skip=1):
#     """
#     Processes each video frame: detects faces, recognizes users, and marks attendance,
#     with emotion, age, and gender prediction.
#     """
#     # Skip frames to optimize performance
#     if frame_skip > 1 and (frame_skip % 2 == 0):
#         return frame  # Skip processing if needed (for every nth frame)
#
#     gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#
#     for (x, y, w, h) in faces:
#         face = gray[y:y + h, x:x + w]
#         face_rgb = frame[y:y + h, x:x + w]
#
#         # Emotion Prediction
#         emotion = "Unknown"
#
#         def emotion_predict():
#             nonlocal emotion
#             try:
#                 emotion_face = cv.resize(face, (48, 48))
#                 emotion_face = emotion_face.astype('float32') / 255
#                 emotion_face = np.expand_dims(emotion_face, axis=0)
#                 emotion_face = np.expand_dims(emotion_face, axis=-1)
#                 emotion_prediction = emotion_model.predict(emotion_face)
#                 emotion = emotion_labels[np.argmax(emotion_prediction[0])]
#             except Exception as e:
#                 print(f"Error in emotion prediction: {e}")
#
#         # Age and Gender Prediction
#         gender, age = "Unknown", "Unknown"
#
#         def age_gender_predict():
#             nonlocal gender, age
#             try:
#                 face_blob = cv.dnn.blobFromImage(face_rgb, 1.0, (227, 227),
#                                                  (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
#                 gender_net.setInput(face_blob)
#                 gender_preds = gender_net.forward()
#                 gender = gender_labels[gender_preds[0].argmax()]
#
#                 age_net.setInput(face_blob)
#                 age_preds = age_net.forward()
#                 age = age_labels[age_preds[0].argmax()]
#             except Exception as e:
#                 print(f"Error in age or gender prediction: {e}")
#
#         # Start emotion and age/gender prediction in parallel using threading
#         emotion_thread = threading.Thread(target=emotion_predict)
#         age_gender_thread = threading.Thread(target=age_gender_predict)
#
#         emotion_thread.start()
#         age_gender_thread.start()
#
#         emotion_thread.join()
#         age_gender_thread.join()
#
#         # Face Recognition using DeepFace
#         recognition_result = recognize_person(face_rgb, db_path=db_path)
#         recognized_person = recognition_result["name"]
#         status = recognition_result["status"]
#
#         # Mark attendance for recognized (registered) users
#         if status == "Registered":
#             mark_attendance(recognized_person)
#
#         # Build info text and adjust color based on recognition status
#         info_text = f'{recognized_person}, {emotion}, {age}, {gender}'
#         color = (0, 255, 0) if status == "Registered" else (0, 0, 255)
#         cv.putText(frame, info_text, (x + 6, y - 6), cv.FONT_HERSHEY_PLAIN, 2, color, 2)
#         cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)
#
#     return frame
#
# def take_usn_input(usn_entry):
#     """Get the USN from the input field, validate the format, and check if the directory exists."""
#     usn = usn_entry.get()
#
#     # Define the regex pattern for the valid USN format
#     usn_pattern = r"^\d{1}[A-Za-z]{2}\d{2}[A-Za-z]{2}\d{3}$"
#
#     # Validate the USN format using the regex
#     if re.match(usn_pattern, usn):
#         # Check if the directory corresponding to the USN exists in the 'facedata' folder
#         usn_directory = os.path.join("facedata", usn)
#         if os.path.exists(usn_directory):
#             return usn
#         else:
#             # Show an error message if the directory doesn't exist
#             MessageBox.showerror("Error", f"No directory found for USN: {usn}")
#             return None
#     else:
#         # Show an error message for invalid USN format
#         MessageBox.showerror("Error", f"Invalid USN format: {usn}. Please use the format '4HG21CS000'.")
#         return None
# # Start camera and integrate with Tkinter
# def start_camera(camera_label,usn_entry):
#     """Starts the camera and integrates with Tkinter."""
#     cap = cv.VideoCapture(0, cv.CAP_DSHOW)
#     usn = take_usn_input(usn_entry);
#     db_path = f"FaceData/{usn}"
#     def update_frame():
#         ret, frame = cap.read()
#         if ret:
#             frame = process_frame(frame, db_path=db_path)
#             # Convert frame to ImageTk format
#             frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#             img = Image.fromarray(frame)
#             imgtk = ImageTk.PhotoImage(image=img)
#             camera_label.imgtk = imgtk
#             camera_label.configure(image=imgtk)
#             camera_label.after(10, update_frame)
#
#     update_frame()
#
#
# # Create the GUI window
# def start_gui():
#     """Creates the main Tkinter window with integrated camera feed."""
#     global root
#     root = tk.Tk()
#     root.title("Face Detection and Attendance System")
#     root.attributes('-fullscreen', True)
#     root.configure(bg="#2d2d2d")
#
#     root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))
#     root.bind("<F11>", lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))
#
#     # Header Frame
#     header_frame = tk.Frame(root, bg="#a11587")
#     header_frame.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)
#
#     header_label = tk.Label(
#         header_frame,
#         text="Attendance System",
#         fg="white",
#         bg="#262523",
#         font=('times', 24, 'bold')
#     )
#     header_label.pack(fill='both', expand=True)
#
#     # Time and Date Label
#     time_label = tk.Label(root, fg="orange", bg="#2d2d2d", font=('times', 20, 'bold'))
#     time_label.place(relx=0.0, rely=0.1, relwidth=1, relheight=0.05)
#
#     def update_time():
#         current_time = time.strftime("%H:%M:%S")
#         current_date = time.strftime("%d/%m/%Y")
#         time_label.config(text=f"Date: {current_date} | Time: {current_time}")
#         time_label.after(1000, update_time)
#
#     update_time()
#
#
#     # Camera Feed Frame
#     camera_label = tk.Label(root, bg="#2d2d2d")
#     camera_label.place(relx=0.0, rely=0.2, relwidth=1, relheight=0.65)
#
#     # Control Buttons Frame
#     buttons_frame = tk.Frame(root, bg="#2d2d2d")
#     buttons_frame.place(relx=0.0, rely=0.85, relwidth=1, relheight=0.15)
#
#     usn_label = tk.Label(buttons_frame, text="Enter USN:", fg="white", bg="#2d2d2d", font=('times', 16))
#     usn_label.pack(side=tk.LEFT, padx=20, pady=20)
#
#     usn_entry = tk.Entry(buttons_frame, font=('times', 16))
#     usn_entry.pack(side=tk.LEFT, padx=20, pady=20)
#
#     # Start Button
#     start_button = ttk.Button(buttons_frame, text="Start Camera", command=lambda: start_camera(camera_label, usn_entry))
#     start_button.pack(side=tk.LEFT, padx=20, pady=20)
#
#     # Exit Button
#     exit_button = ttk.Button(buttons_frame, text="Exit", command=root.destroy)
#     exit_button.pack(side=tk.RIGHT, padx=20, pady=20)
#
#     # Main window loop
#     root.mainloop()
#
#
# if __name__ == "__main__":
#     start_gui()
import tkinter as tk
from tkinter import ttk, messagebox as MessageBox
from PIL import Image, ImageTk
import cv2 as cv
import os
import re
import threading
import time
from datetime import datetime

# Define your cascade and models (assuming these are already loaded)
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

# def process_frame(frame, db_path="FaceData", frame_skip=1):
#     """Processes each video frame: detects faces, recognizes users, and marks attendance,
#     with emotion prediction.
#     """
#     # Skip frames to optimize performance
#     if frame_skip > 1 and (frame_skip % 2 == 0):
#         return frame  # Skip processing if needed (for every nth frame)
#
#     gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#
#     for (x, y, w, h) in faces:
#         face = gray[y:y + h, x:x + w]
#         face_rgb = frame[y:y + h, x:x + w]
#
#         # Emotion Prediction
#         emotion = "Unknown"
#
#         def emotion_predict():
#             nonlocal emotion
#             try:
#                 emotion_face = cv.resize(face, (48, 48))
#                 emotion_face = emotion_face.astype('float32') / 255
#                 emotion_face = np.expand_dims(emotion_face, axis=0)
#                 emotion_face = np.expand_dims(emotion_face, axis=-1)
#                 emotion_prediction = emotion_model.predict(emotion_face)
#                 emotion = emotion_labels[np.argmax(emotion_prediction[0])]
#             except Exception as e:
#                 print(f"Error in emotion prediction: {e}")
#
#         # Start emotion prediction in a separate thread
#         emotion_thread = threading.Thread(target=emotion_predict)
#         emotion_thread.start()
#
#         emotion_thread.join()
#
#         # Face Recognition using DeepFace
#         recognition_result = recognize_person(face_rgb, db_path=db_path)
#         recognized_person = recognition_result["name"]
#         status = recognition_result["status"]
#
#         # Mark attendance for recognized (registered) users
#         if status == "Registered":
#             mark_attendance(recognized_person)
#
#         # Return the recognized data (used for display below camera)
#         info_text = f'{recognized_person}, {emotion}'
#         return info_text, status
#
#     return None, None  # Return None if no face is detected
# def process_frame(frame,db_path="FaceData", frame_skip=1):
#     """Processes each video frame: detects faces, recognizes users from the entered USN directory, and marks attendance,
#     with emotion prediction."""
#
#     # Skip frames to optimize performance
#     if frame_skip > 1 and (frame_skip % 2 == 0):
#         return frame  # Skip processing if needed (for every nth frame)
#
#     # Assuming `usn` is already validated in `take_usn_input` and passed into the function
#     usn_directory = os.path.join(db_path)  # Path to the USN directory
#
#     gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#
#     for (x, y, w, h) in faces:
#         face = gray[y:y + h, x:x + w]
#         face_rgb = frame[y:y + h, x:x + w]
#
#         # Emotion Prediction
#         emotion = "Unknown"
#
#         def emotion_predict():
#             nonlocal emotion
#             try:
#                 emotion_face = cv.resize(face, (48, 48))
#                 emotion_face = emotion_face.astype('float32') / 255
#                 emotion_face = np.expand_dims(emotion_face, axis=0)
#                 emotion_face = np.expand_dims(emotion_face, axis=-1)
#                 emotion_prediction = emotion_model.predict(emotion_face)
#                 emotion = emotion_labels[np.argmax(emotion_prediction[0])]
#             except Exception as e:
#                 print(f"Error in emotion prediction: {e}")
#
#         # Start emotion prediction in a separate thread
#         emotion_thread = threading.Thread(target=emotion_predict)
#         emotion_thread.start()
#
#         emotion_thread.join()
#
#         # Face Recognition using DeepFace with the specific USN directory
#         recognition_result = recognize_person(face_rgb, db_path=usn_directory)  # Pass only the user's directory
#         recognized_person = recognition_result["name"]
#         status = recognition_result["status"]
#
#         # Mark attendance for recognized (registered) users
#         if status == "Registered":
#             mark_attendance(recognized_person)
#
#         # Return the recognized data (used for display below camera)
#         info_text = f'{recognized_person}, {emotion}'
#         return info_text, status
#
#     return None, None  # Return None if no face is detected
def process_frame(frame, db_path="FaceData", frame_skip=1):
    """Processes each video frame: detects faces, recognizes users from the entered USN directory, and marks attendance,
    with emotion prediction. Displays creative lines for both recognized and unknown persons, ensuring variety daily."""

    # Skip frames to optimize performance
    if frame_skip > 1 and (frame_skip % 2 == 0):
        return frame  # Skip processing if needed (for every nth frame)

    # Path to the USN directory
    usn_directory = os.path.join(db_path)  # Path to the USN directory

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y + h, x:x + w]
        face_rgb = frame[y:y + h, x:x + w]

        # Emotion Prediction
        emotion = "Unknown"

        def emotion_predict():
            nonlocal emotion
            try:
                emotion_face = cv.resize(face, (48, 48))
                emotion_face = emotion_face.astype('float32') / 255
                emotion_face = np.expand_dims(emotion_face, axis=0)
                emotion_face = np.expand_dims(emotion_face, axis=-1)
                emotion_prediction = emotion_model.predict(emotion_face)
                emotion = emotion_labels[np.argmax(emotion_prediction[0])]
            except Exception as e:
                print(f"Error in emotion prediction: {e}")

        # Start emotion prediction in a separate thread
        emotion_thread = threading.Thread(target=emotion_predict)
        emotion_thread.start()
        emotion_thread.join()

        # Face Recognition using DeepFace with the specific USN directory
        recognition_result = recognize_person(face_rgb, db_path=usn_directory)  # Pass only the user's directory
        recognized_person = recognition_result["name"]
        status = recognition_result["status"]

        # Creative lines based on detected emotion
        creative_lines = {
            "happy": ["You're glowing with joy today!", "Keep smiling, it's contagious!", "Happiness suits you well!"],
            "sad": ["Cheer up, better days are ahead!", "It's okay to feel down sometimes, you're strong!",
                    "Take a deep breath, everything will be alright."],
            "angry": ["Take a deep breath, let's calm down.", "Channel that energy into something positive!",
                      "Anger fades away, let's turn it into motivation."],
            "surprised": ["Wow, that was an unexpected look!", "You caught me off guard, are you okay?",
                          "Surprise is the spice of life!"],
            "neutral": ["You look calm and collected.", "Steady as usual, I see.", "Feeling balanced today?"],
            "fear": ["Stay strong, you're capable of facing anything.", "Fear is just temporary, you've got this.",
                     "Take control, you're braver than you think."]
        }

        # Function to select a random line based on user and date
        def select_unique_line(person_name, emotion):
            # Use a combination of the person's name (or "Unknown") and the current date to generate a seed
            today = datetime.today().strftime('%Y-%m-%d')  # Get today's date
            seed = f"{person_name}_{today}_{emotion}"
            # Generate a hash from the seed to ensure uniqueness
            hash_value = int(hashlib.md5(seed.encode()).hexdigest(), 16)
            random.seed(hash_value)  # Set the seed for random selection
            # Select a random line for the given emotion
            return random.choice(creative_lines.get(emotion.lower(), ["Stay awesome!"]))

        # Handle recognized and unrecognized persons
        person_name = recognized_person if status == "Registered" else "Unknown Person"

        # Get a unique creative line based on the person and emotion
        creative_message = select_unique_line(person_name, emotion)

        # Update info text with recognition, emotion, and creative message
        info_text = f'{person_name}, {emotion} - {creative_message}'

        # If recognized, mark attendance
        if status == "Registered":
            mark_attendance(recognized_person)

        # Return the info text for display
        return info_text, status

    # Return None if no face is detected
    return None, None


def take_usn_input(usn_entry):
    """Get the USN from the input field, validate the format, and check if the directory exists."""
    usn = usn_entry.get()

    # Define the regex pattern for the valid USN format
    usn_pattern = r"^\d{1}[A-Za-z]{2}\d{2}[A-Za-z]{2}\d{3}$"

    # Validate the USN format using the regex
    if re.match(usn_pattern, usn):
        # Check if the directory corresponding to the USN exists in the 'facedata' folder
        usn_directory = os.path.join("facedata", usn)
        if os.path.exists(usn_directory):
            return usn
        else:
            # Show an error message if the directory doesn't exist
            MessageBox.showerror("Error", f"No USN found for USN: {usn}")
            return None
    else:
        # Show an error message for invalid USN format
        MessageBox.showerror("Error", f"Invalid USN format: {usn}. Please use the format '4HG21CS000'.")
        return None

# Start camera and integrate with Tkinter
# def start_camera(camera_label, info_label, usn_entry):
#     """Starts the camera and integrates with Tkinter."""
#     cap = cv.VideoCapture(0, cv.CAP_DSHOW)
#     usn = take_usn_input(usn_entry)
#     if not usn:
#         return
#
#     db_path = f"FaceData/{usn}"
#
#     def update_frame():
#         ret, frame = cap.read()
#         if ret:
#             info_text, status = process_frame(frame, db_path=db_path)
#
#             # If a person is recognized, update the label with the info
#             if info_text:
#                 color = "green" if status == "Registered" else "red"
#                 info_label.config(text=info_text, fg=color)
#
#             # Convert frame to ImageTk format
#             frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#             img = Image.fromarray(frame)
#             imgtk = ImageTk.PhotoImage(image=img)
#             camera_label.imgtk = imgtk
#             camera_label.configure(image=imgtk)
#
#             camera_label.after(10, update_frame)
#
#     update_frame()
def start_camera(camera_label, info_label, usn_entry):
    """Starts the camera and integrates with Tkinter."""
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    usn = take_usn_input(usn_entry)  # Get the validated USN
    if not usn:
        return  # If usn is None, return early (invalid USN or directory)

    db_path = f"FaceData/{usn}"

    def update_frame():
        ret, frame = cap.read()
        if ret:
            # Pass both db_path and usn to process_frame
            info_text, status = process_frame(frame,db_path=db_path)

            # If a person is recognized, update the label with the info
            if info_text:
                color = "green" if status == "Registered" else "red"
                info_label.config(text=info_text, fg=color)

            # Convert frame to ImageTk format for display
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)

            camera_label.after(10, update_frame)

    update_frame()



# Create the GUI window
def start_gui():
    """Creates the main Tkinter window with integrated camera feed."""
    global root
    root = tk.Tk()
    root.title("Face Detection and Attendance System")
    root.attributes('-fullscreen', True)
    root.configure(bg="#2d2d2d")

    root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))
    root.bind("<F11>", lambda e: root.attributes('-fullscreen', not root.attributes('-fullscreen')))

    # Header Frame
    header_frame = tk.Frame(root, bg="#a11587")
    header_frame.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)

    header_label = tk.Label(
        header_frame,
        text="Attendance System",
        fg="white",
        bg="#262523",
        font=('times', 24, 'bold')
    )
    header_label.pack(fill='both', expand=True)

    # Time and Date Label
    time_label = tk.Label(root, fg="orange", bg="#2d2d2d", font=('times', 20, 'bold'))
    time_label.place(relx=0.0, rely=0.1, relwidth=1, relheight=0.05)

    def update_time():
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d/%m/%Y")
        time_label.config(text=f"Date: {current_date} | Time: {current_time}")
        time_label.after(1000, update_time)

    update_time()

    # Camera Feed Frame
    camera_label = tk.Label(root, bg="#2d2d2d")
    camera_label.place(relx=0.0, rely=0.2, relwidth=1, relheight=0.6)

    # Info Display Frame (below the camera)
    info_label = tk.Label(root, text="", fg="black", bg="#2d2d2d", font=('times', 16))
    info_label.place(relx=0.0, rely=0.8, relwidth=1, relheight=0.1)

    # Control Buttons Frame (fixed size at the bottom)
    buttons_frame = tk.Frame(root, bg="#2d2d2d")
    buttons_frame.place(relx=0.0, rely=0.9, relwidth=1, relheight=0.1)

    usn_label = tk.Label(buttons_frame, text="Enter USN:", fg="white", bg="#2d2d2d", font=('times', 16))
    usn_label.pack(side=tk.LEFT, padx=20, pady=10)

    usn_entry = tk.Entry(buttons_frame, font=('times', 16))
    usn_entry.pack(side=tk.LEFT, padx=20, pady=10)

    # Start Button
    start_button = ttk.Button(buttons_frame, text="Start Camera", command=lambda: start_camera(camera_label, info_label, usn_entry))
    start_button.pack(side=tk.LEFT, padx=20, pady=10)

    # Exit Button
    exit_button = ttk.Button(buttons_frame, text="Exit", command=root.destroy)
    exit_button.pack(side=tk.RIGHT, padx=20, pady=10)

    # Main window loop
    root.mainloop()


if __name__ == "__main__":
    start_gui()

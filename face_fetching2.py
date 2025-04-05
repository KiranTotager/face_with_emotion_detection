import tkinter as tk
from tkinter import messagebox
import cv2 as cv
import os
from PIL import Image, ImageTk
import time
import re
from tkcalendar import DateEntry
import sqlite3
import mysql.connector
from mysql.connector import Error
import subprocess
from datetime import datetime
# def fetch_faces_gui(name, camera_label, result_label):
#     """Captures face images using the webcam and saves them in a directory."""
#     cap = cv.VideoCapture(0)
#
#     if not cap.isOpened():
#         messagebox.showerror("Camera Error", "Unable to access the camera.")
#         return
#
#     face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
#
#     dir_ = "FaceData"
#
#     # Ensure the directory for face data exists
#     if not os.path.exists(dir_):
#         os.mkdir(dir_)
#
#     user_folder = os.path.join(dir_, name)
#
#     # If the folder doesn't exist, create it
#     if not os.path.exists(user_folder):
#         os.mkdir(user_folder)
#
#     id_ = 0
#
#     def capture_frame():
#         nonlocal id_
#
#         if id_ >= 100:
#             result_label.config(text="Face collection complete!", fg="green")
#             # Result Label - Place at the bottom of the window
#             cap.release()
#             cv.destroyAllWindows()
#             return
#
#         ret, frame = cap.read()
#         if not ret:
#             messagebox.showerror("Capture Error", "Error capturing image.")
#             return
#
#         gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
#
#         # Save the image with a filename
#         filename = os.path.join(user_folder, f"img{id_}.png")
#         cv.imwrite(filename, gray)
#         id_ += 1
#
#         # Display the webcam feed in the camera_label
#         frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
#         img = Image.fromarray(frame_rgb)
#         imgtk = ImageTk.PhotoImage(image=img)
#         camera_label.imgtk = imgtk
#         camera_label.configure(image=imgtk)
#         camera_label.place(relx=0.6, rely=0.3, relwidth=0.4, relheight=0.4)
#
#         # Schedule the next frame capture
#         camera_label.after(10, capture_frame)
#
#     capture_frame()
def fetch_faces_gui(usn, camera_label, result_label):
    """Captures face images using the webcam and saves them in a directory."""
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Unable to access the camera.")
        return

    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

    dir_ = "FaceData"

    # Ensure the directory for face data exists
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    user_folder = os.path.join(dir_, usn)

    # If the folder doesn't exist, create it
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)

    id_ = 0

    def capture_frame():
        nonlocal id_

        if id_ >= 100:
            result_label.config(text="Face collection complete!", fg="green")
            # Result Label - Place at the bottom of the window
            cap.release()
            cv.destroyAllWindows()
            return

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Capture Error", "Error capturing image.")
            return

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Save the image with a filename
        filename = os.path.join(user_folder, f"img{id_}.png")
        cv.imwrite(filename, gray)
        id_ += 1

        # Display the webcam feed in the camera_label
        frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)
        camera_label.place(relx=0.6, rely=0.3, relwidth=0.4, relheight=0.4)

        # Schedule the next frame capture
        camera_label.after(10, capture_frame)

    capture_frame()

# def start_face_fetching(txt_name, camera_label, result_label):
#     """Handles the 'Take Images' button click."""
#     img_name = txt_name.get()
#
#     if not img_name or img_name == "Enter your name":  # Assuming "Enter your name" is the placeholder text
#         messagebox.showerror("Input Error", "Please enter a name before proceeding.")
#         return  # Prevent further execution if the name is empty or placeholder
#
#     result_label.config(text="Capturing faces...", fg="green")
#
#     # Start the face fetching process and show the camera feed in the same window
#     fetch_faces_gui(img_name, camera_label, result_label)
# def start_face_fetching(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB, camera_label, result_label):
#     """Handles the 'Take Images' button click."""
#     img_name = txt_name.get()
#     img_usn = txt_usn.get()
#     img_branch = txt_branch.get()
#     img_sem = txt_sem.get()
#     img_dob = txt_DOB.get()
#
#     if not img_name or img_name == "Enter your name":  # Ensure name is entered
#         messagebox.showerror("Input Error", "Please enter a name before proceeding.")
#         return  # Prevent further execution if the name is empty or placeholder
#
#     if not img_usn or not img_branch or not img_sem or not img_dob:  # Ensure all fields are filled
#         messagebox.showerror("Input Error", "Please fill in all fields before proceeding.")
#         return
#
#     result_label.config(text="Capturing faces...", fg="green")
#
#     # Insert user details into the database
#     conn = sqlite3.connect('User_details.db')
#     c = conn.cursor()
#
#     # Insert the user details into the database
#     c.execute('''INSERT INTO users (name, usn, branch, semester, dob, face_data_path)
#                  VALUES (?, ?, ?, ?, ?, ?)''',
#               (img_name, img_usn, img_branch, img_sem, img_dob, "FaceData/" + img_name))
#     conn.commit()
#     conn.close()
#
#     # Start the face fetching process and show the camera feed in the same window
#     fetch_faces_gui(img_name, camera_label, result_label)
# def start_face_fetching(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB, camera_label, result_label):
#     """Handles the 'Take Images' button click."""
#     img_name = txt_name.get()
#     img_usn = txt_usn.get()
#     img_branch = txt_branch.get()
#     img_sem = txt_sem.get()
#     img_dob = txt_DOB.get()
#
#     if not img_name or img_name == "Enter your name":  # Ensure name is entered
#         messagebox.showerror("Input Error", "Please enter a name before proceeding.")
#         return  # Prevent further execution if the name is empty or placeholder
#
#     if not img_usn or not img_branch or not img_sem or not img_dob:  # Ensure all fields are filled
#         messagebox.showerror("Input Error", "Please fill in all fields before proceeding.")
#         return
#
#     result_label.config(text="Capturing faces...", fg="green")
#
#     # Insert user details into the database
#     conn = sqlite3.connect('User_details.db')
#     c = conn.cursor()
#
#     # Create the 'users' table if it doesn't exist
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             usn TEXT NOT NULL,
#             branch TEXT NOT NULL,
#             semester TEXT NOT NULL,
#             dob TEXT NOT NULL,
#             face_data_path TEXT NOT NULL
#         )
#     ''')
#
#     # Insert the user details into the database
#     c.execute('''INSERT INTO users (name, usn, branch, semester, dob, face_data_path)
#                  VALUES (?, ?, ?, ?, ?, ?)''',
#               (img_name, img_usn, img_branch, img_sem, img_dob, "FaceData/" + img_name))
#     conn.commit()
#     conn.close()
#
#     # Start the face fetching process and show the camera feed in the same window
#     fetch_faces_gui(img_name, camera_label, result_label)
import sqlite3
from tkinter import messagebox

# def start_face_fetching(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB, camera_label, result_label):
#     """Handles the 'Take Images' button click."""
#     img_name = txt_name.get()
#     img_usn = txt_usn.get()
#     img_branch = txt_branch.get()
#     img_sem = txt_sem.get()
#     img_dob = txt_DOB.get()
#
#     # Ensure all required fields are filled
#     if not img_name or img_name == "Enter your name":  # Ensure name is entered
#         messagebox.showerror("Input Error", "Please enter a name before proceeding.")
#         return  # Prevent further execution if the name is empty or placeholder
#
#     if not img_usn or not img_branch or not img_sem or not img_dob:  # Ensure all fields are filled
#         messagebox.showerror("Input Error", "Please fill in all fields before proceeding.")
#         return
#
#     # Connect to the database
#     conn = sqlite3.connect('User_details.db')
#     c = conn.cursor()
#
#     # Check if user with the same USN already exists
#     c.execute('SELECT * FROM users WHERE usn = ?', (img_usn,))
#     existing_user = c.fetchone()
#
#     if existing_user:
#         messagebox.showerror("User Exists", f"A user with USN {img_usn} already exists.")
#         conn.close()
#         return
#
#     # Create the 'users' table if it doesn't exist
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             usn TEXT NOT NULL,
#             branch TEXT NOT NULL,
#             semester TEXT NOT NULL,
#             dob TEXT NOT NULL,
#             face_data_path TEXT NOT NULL
#         )
#     ''')
#
#     # Insert the user details into the database
#     c.execute('''INSERT INTO users (name, usn, branch, semester, dob, face_data_path)
#                  VALUES (?, ?, ?, ?, ?, ?)''',
#               (img_name, img_usn, img_branch, img_sem, img_dob, "FaceData/" + img_name))
#     conn.commit()
#     conn.close()
#     clear_name_entry(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB)
#
#     # Update the result label and proceed with capturing faces
#     result_label.config(text="Capturing faces...", fg="green")
#     fetch_faces_gui(img_usn, camera_label, result_label)
# def start_face_fetching(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB, camera_label, result_label):
#     """Handles the 'Take Images' button click."""
#     img_name = txt_name.get()
#     img_usn = txt_usn.get()
#     img_branch = txt_branch.get()
#     img_sem = txt_sem.get()
#     img_dob = txt_DOB.get()
#
#     # Ensure all required fields are filled
#     if not img_name or img_name == "Enter your name":  # Ensure name is entered
#         messagebox.showerror("Input Error", "Please enter a name before proceeding.")
#         return  # Prevent further execution if the name is empty or placeholder
#
#     if not img_usn or not img_branch or not img_sem or not img_dob:  # Ensure all fields are filled
#         messagebox.showerror("Input Error", "Please fill in all fields before proceeding.")
#         return
#
#     # Retry logic for handling database locked error
#     retry_count = 5
#     while retry_count > 0:
#         try:
#             with sqlite3.connect('User_details.db') as conn:
#                 conn.execute("PRAGMA journal_mode=WAL;")
#                 c = conn.cursor()
#
#                 # Check if user with the same USN already exists
#                 c.execute('SELECT * FROM users WHERE usn = ?', (img_usn,))
#                 existing_user = c.fetchone()
#
#                 if existing_user:
#                     messagebox.showerror("User Exists", f"A user with USN {img_usn} already exists.")
#                     return
#
#                 # Create the 'users' table if it doesn't exist
#                 c.execute('''
#                     CREATE TABLE IF NOT EXISTS users (
#                         id INTEGER PRIMARY KEY AUTOINCREMENT,
#                         name TEXT NOT NULL,
#                         usn TEXT NOT NULL,
#                         branch TEXT NOT NULL,
#                         semester TEXT NOT NULL,
#                         dob TEXT NOT NULL,
#                         face_data_path TEXT NOT NULL
#                     )
#                 ''')
#
#                 # Insert the user details into the database
#                 c.execute('''INSERT INTO users (name, usn, branch, semester, dob, face_data_path)
#                              VALUES (?, ?, ?, ?, ?, ?)''',
#                           (img_name, img_usn, img_branch, img_sem, img_dob, "FaceData/" + img_usn))
#                 conn.commit()
#
#             # Clear the name entry after storing data in the database
#             clear_name_entry(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB)
#
#             # Update the result label and proceed with capturing faces
#             result_label.config(text="Capturing faces...", fg="green")
#             fetch_faces_gui(img_usn, camera_label, result_label)
#
#             break  # Break out of the loop if successful
#
#         except sqlite3.OperationalError as e:
#             # If the database is locked, retry a few times
#             retry_count -= 1
#             if retry_count == 0:
#                 messagebox.showerror("Database Error", "The database is locked. Please try again later.")
#                 break
#             else:
#                 # Wait for 1 second before retrying
#                 time.sleep(1)
def start_face_fetching(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB, camera_label, result_label):
    """Handles the 'Take Images' button click."""
    img_name = txt_name.get()
    img_usn = txt_usn.get()
    img_branch = txt_branch.get()
    img_sem = txt_sem.get()
    selected_date = txt_DOB.get_date()
    img_dob = selected_date.strftime("%Y-%m-%d")
    # print("date is",img_dob)

    # Ensure all required fields are filled
    if not img_name or img_name == "Enter your name":  # Ensure name is entered
        messagebox.showerror("Input Error", "Please enter a name before proceeding.")
        return

    if not img_usn or not img_branch or not img_sem or not img_dob:
        messagebox.showerror("Input Error", "Please fill in all fields before proceeding.")
        return

    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',  # Replace with your MySQL server address
            user='root',       # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='AttendanceSystem'  # Replace with your database name
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Check if user with the same USN already exists
            cursor.execute('SELECT * FROM users WHERE usn = %s', (img_usn,))
            existing_user = cursor.fetchone()

            if existing_user:
                messagebox.showerror("User Exists", f"A user with USN {img_usn} already exists.")
                return

            # Create the 'users' table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    usn VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    branch VARCHAR(255) NOT NULL,
                    semester VARCHAR(255) NOT NULL,
                    dob DATE NOT NULL,
                    face_data_path VARCHAR(255) NOT NULL
                )
            ''')

            # Insert the user details into the database
            cursor.execute('''
                INSERT INTO users (name, usn, branch, semester, dob, face_data_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (img_name, img_usn, img_branch, img_sem, img_dob, "FaceData/" + img_usn))
            connection.commit()

            # Clear the name entry after storing data in the database
            clear_name_entry(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB)

            # Update the result label and proceed with capturing faces
            result_label.config(text="Capturing faces...", fg="green")
            fetch_faces_gui(img_usn, camera_label, result_label)

    except Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def clear_name_entry(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB):
    """Clear the name entry field."""
    txt_name.delete(0, tk.END)
    txt_usn.delete(0,tk.END)
    txt_branch.delete(0,tk.END)
    txt_sem.delete(0,tk.END)
    txt_DOB.delete(0,tk.END)

def update_time():
    """Updates the time and date label every second."""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    time_label.config(text=f"Date: {time.strftime('%d/%m/%Y')} | Time: {current_time}")
    time_label.after(1000, update_time)  # Update every second

# Main GUI window
root = tk.Tk()
root.title("Face Fetching GUI")
root.geometry("1600x900")  # Adjusted to make space for time label
root.configure(bg="#2d2d2d")

# Header
header_label = tk.Label(
    root,
    text="Face Fetching System",
    bg="#2d2d2d",
    fg="white",
    font=('Arial', 24, 'bold')
)
header_label.pack(pady=20)

# Time and Date display frame
time_frame = tk.Frame(root, bg="#2d2d2d")
time_frame.pack(fill="x", pady=5)  # Place at top of window with some padding

time_label = tk.Label(time_frame, bg="#2d2d2d", fg="white", font=('Arial', 14))
time_label.pack()

# Name input field (from your code)
# input_frame = tk.Frame(root, bg="#2d2d2d")
# input_frame.pack(pady=10)
#
# label_name = tk.Label(input_frame, text="Enter Name", width=20, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
# label_name.grid(row=0, column=0, padx=10, pady=5)
#
# txt_name = tk.Entry(input_frame, font=('Arial', 16))
# txt_name.grid(row=0, column=1, padx=10, pady=5)
#
# clear_button = tk.Button(input_frame, text="Clear", command=lambda: clear_name_entry(txt_name), fg="black", bg="#ea2a2a", width=11, font=('times', 11, 'bold'))
# clear_button.grid(row=1, column=1, padx=10, pady=5)
#
# # Buttons
# button_frame = tk.Frame(root, bg="#2d2d2d")
# button_frame.pack(pady=20)
#
# start_button = tk.Button(button_frame, text="Take Images", command=lambda: start_face_fetching(txt_name, camera_label, result_label), bg="orange", fg="white", width=25, height=1, font=('times', 15, 'bold'))
# start_button.pack(side="left", padx=10)
#
# exit_button = tk.Button(button_frame, text="Exit", command=root.destroy, bg="red", fg="white", width=25, height=1, font=('times', 15, 'bold'))
# exit_button.pack(side="right", padx=10)

# Left Frame for inputs and buttons
left_frame = tk.Frame(root, bg="#2d2d2d")
left_frame.pack(side="left", fill="y", padx=20, pady=20)

# Name Input Fields
# label_name = tk.Label(left_frame, text="Enter Name :", width=10, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
# label_name.pack(pady=10, anchor="w")  # Anchor aligns to the left within the frame
#
# txt_name = tk.Entry(left_frame, font=('Arial', 16))
# txt_name.pack(padx=170,pady=10, anchor="w")
# Left Frame for inputs and buttons
# left_frame = tk.Frame(root, bg="#2d2d2d")
# left_frame.pack(side="left", fill="y", padx=20, pady=20)
left_frame = tk.Frame(root, bg="#2d2d2d", width=2000)  # Set the width of the left_frame
left_frame.pack(side="left", fill="y", padx=20, pady=20)

# Enter Name Label and Entry Side by Side Using place
label_name = tk.Label(left_frame, text="Enter Name :", width=10, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
label_name.place(x=10, y=10)  # Precise position for the label

txt_name = tk.Entry(left_frame, font=('Arial', 16))
txt_name.place(x=170, y=10, width=400, height=30)  # This will place the entry widget correctly with width 800
  # Positioned right of the label

# label_usn = tk.Label(left_frame, text="Enter USN :", width=10, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
# label_usn.place(x=10, y=70)  # Precise position for the label
#
# txt_usn = tk.Entry(left_frame, font=('Arial', 16))
# txt_usn.place(x=170, y=70, width=400, height=30)  # Positioned right of the label

label_branch = tk.Label(left_frame, text="Enter Branch :", width=10, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
label_branch.place(x=10, y=120)  # Precise position for the label

txt_branch = tk.Entry(left_frame, font=('Arial', 16))
txt_branch.place(x=170, y=120, width=400, height=30)  # Positioned right of the label

label_sem = tk.Label(left_frame, text="Enter sem :", width=10, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
label_sem.place(x=10, y=170)  # Precise position for the label

txt_sem= tk.Entry(left_frame, font=('Arial', 16))
txt_sem.place(x=170, y=170, width=400, height=30)  # Positioned right of the label

label_DOB = tk.Label(left_frame, text="Enter DOB :", width=10, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
label_DOB.place(x=10, y=220)  # Precise position for the label

# txt_DOB = tk.Entry(left_frame, font=('Arial', 16))
# txt_DOB.place(x=170, y=220, width=400, height=30)  # Positioned right of the label
# txt_DOB = DateEntry(left_frame, width=12, background='darkblue', foreground='white', borderwidth=2, font=('times', 15))
# txt_DOB.place(x=170, y=220, width=400, height=30)
# Define the DateEntry widget
txt_DOB = DateEntry(
    left_frame,
    width=12,
    background='darkblue',
    foreground='white',
    borderwidth=2,
    font=('times', 15),
    date_pattern='yyyy-mm-dd'  # Ensures the display format is also yyyy-mm-dd
)
txt_DOB.place(x=170, y=220, width=400, height=30)
# print("the date is",txt_DOB)

# clear_button = tk.Button(left_frame, text="Clear", command=lambda: clear_name_entry(txt_name), fg="black", bg="#ea2a2a", width=11, font=('times', 11, 'bold'))
# clear_button.pack(pady=100, anchor="w")
#
# # Buttons
# start_button = tk.Button(left_frame, text="Take Images", command=lambda: start_face_fetching(txt_name, camera_label, result_label), bg="orange", fg="white", width=25, height=1, font=('times', 15, 'bold'))
# start_button.pack(pady=10, anchor="w")
#
# exit_button = tk.Button(left_frame, text="Exit", command=root.destroy, bg="red", fg="white", width=25, height=1, font=('times', 15, 'bold'))
# exit_button.pack(pady=10, anchor="w")
# Define a position for buttons below the DOB entry widget
button_y_position = 270  # Set this y-position to be just below the txt_DOB (adjust as needed)

# Create the Clear button and place it below the txt_DOB widget
clear_button = tk.Button(left_frame, text="Clear", command=lambda: clear_name_entry(txt_name, txt_usn, txt_branch, txt_sem, txt_DOB), fg="black", bg="#ea2a2a", width=11, font=('times', 11, 'bold'))
clear_button.place(x=170, y=button_y_position)  # Positioning based on y_position

# Create the Take Images button and place it below the Clear button
# start_button = tk.Button(left_frame, text="Take Images", command=lambda: start_face_fetching(txt_name, camera_label, result_label), bg="orange", fg="white", width=25, height=1, font=('times', 15, 'bold'))
start_button = tk.Button(
    left_frame,
    text="Take Images",
    command=lambda: start_face_fetching(
        txt_name, txt_usn, txt_branch, txt_sem, txt_DOB, camera_label, result_label
    ),
    bg="orange", fg="white", width=25, height=1, font=('times', 15, 'bold')
)
start_button.place(x=170, y=button_y_position + 50)  # Adjust y by 50 for spacing

def execute_face_sample_train():
    """Function to execute the face_sample_train.py script."""
    try:
        subprocess.run(["python", "face_sample_train3.py"], check=True)
        print("face_sample_train3.py executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing face_sample_train3.py: {e}")
    root.destroy()  # Close the application window after execution

# button_y_position = 200  # Example y-position for button placement
save_profile_button = tk.Button(
    left_frame,
    text="Save Profile",
    command=execute_face_sample_train,
    bg="green",
    fg="white",
    width=25,
    height=1,
    font=('times', 15, 'bold')
)
save_profile_button.place(x=170, y=button_y_position + 100)  # Adjust y by 100 for spacing
# Create the Exit button and place it below the Take Images button
exit_button = tk.Button(left_frame, text="Exit", command=root.destroy, bg="red", fg="white", width=25, height=1, font=('times', 15, 'bold'))
exit_button.place(x=170, y=button_y_position + 150)  # Adjust y by 100 for spacing

# Result Label
result_label = tk.Label(root, text="", bg="#2d2d2d", fg="white", font=('Arial', 14))
result_label.pack(pady=20)

# Camera label for showing the video feed
camera_label = tk.Label(root, bg="#2d2d2d")
camera_label.pack(fill="both", expand=True)
result_label = tk.Label(root, text="", bg="#2d2d2d", fg="white", font=('Arial', 14))
result_label.pack(side="bottom", pady=50)  # Place it at the bottom with some padding
# Start updating time
update_time()

usn_pattern = r"^[4][A-Z]{2}\d{2}[A-Z]{2}\d{3}$"

def validate_usn_input(P):
    """Validates the USN input against the pattern"""
    if not re.match(usn_pattern, P):
        messagebox.showerror("Invalid USN", "Please enter a valid USN in the format '4HG21CS000'.")
        return False
    return True
validate_usn_input_func = root.register(validate_usn_input)

# USN Entry widget with validation
txt_usn = tk.Entry(left_frame, validate="focusout", validatecommand=(validate_usn_input_func, '%P'), font=('times', 15))

# Create the label and position it
label_usn = tk.Label(left_frame, text="Enter USN :", width=10, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
label_usn.place(x=10, y=70)  # Precise position for the label

# Position the input field
txt_usn.place(x=170, y=70, width=400, height=30)  # Positioned right of the label


root.mainloop()

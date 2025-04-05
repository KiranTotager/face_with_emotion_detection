import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import subprocess
import cv2
import tensorflow as tf
from PIL import Image, ImageTk
import os
import sys
import time
from tkinter import Canvas
                    
# Function to reset terminal output (in case you need to turn on printing later)
def reset_terminal_output():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

# Function to display contact information (help menu)
def contact():
    print("Contact Us: email@example.com")

# def clear():
    # Function to clear text fields
    # txt_id.delete(0, 'end')
    # txt_name.delete(0, 'end')

def track_attendance():
    # This function will execute face_attend.py when the button is clicked.
    print("Taking attendance...")  # This will be suppressed, no output will be printed
    try:
        # Run the face_attend.py script in the background
        subprocess.Popen(["python", "face_attend6.py"])
    except FileNotFoundError:
        print("face_attend6.py file not found. Please make sure it's in the same directory.")
    # Start the camera feed in the Tkinter window
    start_camera()

def start_camera():

    cap = cv2.VideoCapture(0)

    # Function to update the camera feed on the Tkinter window
    def update_frame():
        ret, frame = cap.read()
        if ret:
            # Convert the image from BGR to RGB (Tkinter uses RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert image to ImageTk format for Tkinter
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)

            # Update the label with the new image
            camera_label.img = img
            camera_label.config(image=img)

        # Continue updating the frame every 10ms
        camera_label.after(10, update_frame)

    # Create a Label widget to hold the video feed
    camera_label.place(x=500, y=150, width=640, height=360)

    # Start updating the camera feed
    update_frame()

# Function to open the admin login window
def admin_login():
    # Create a new top-level window for login
    login_window = tk.Toplevel(window)
    login_window.geometry("400x300")  # Increased window size
    login_window.title("Admin Login")
    login_window.config(bg="#00aeff")  # Background color for login window

    # Add a label for the title of the login window
    title_label = tk.Label(login_window, text="Admin Login", font=('times', 18, 'bold'), bg="#00aeff", fg="white")
    title_label.pack(pady=20)

    # Create a frame to hold the form (to make it cleaner)
    form_frame = tk.Frame(login_window, bg="#00aeff")
    form_frame.pack(pady=20)

    # Username Label and Entry
    label_username = tk.Label(form_frame, text="Username", font=('times', 14), bg="#00aeff", fg="white")
    label_username.grid(row=0, column=0, padx=10, pady=5)

    entry_username = tk.Entry(form_frame, font=('times', 14), width=20)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    # Password Label and Entry
    label_password = tk.Label(form_frame, text="Password", font=('times', 14), bg="#00aeff", fg="white")
    label_password.grid(row=1, column=0, padx=10, pady=5)

    entry_password = tk.Entry(form_frame, show="*", font=('times', 14), width=20)
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    # Function to verify admin credentials
    def verify_admin():
        username = entry_username.get()
        password = entry_password.get()

        # Replace with actual admin credentials
        admin_username = "kiran"
        admin_password = "kiran123"  # You can change this to any password

        if username == admin_username and password == admin_password:
            login_window.destroy()  # Close the login window
            print("verified")
            switch_to_admin_panel()  # Switch to admin panel
        else:
            messagebox.showerror("Invalid credentials", "The username or password is incorrect.")
            # Clear the fields after showing the error
            entry_username.delete(0, 'end')
            entry_password.delete(0, 'end')

    # Create a Login Button
    login_button = tk.Button(login_window, text="Login", font=('times', 16, 'bold'), command=verify_admin,
                             bg="#4CAF50", fg="white", relief="flat", width=15)
    login_button.pack(pady=20)

    # Function to switch to the admin panel
    def switch_to_admin_panel():
        # Switch to the Admin Panel tab
        print("executing")
        notebook.select(right_frame)



# Initialize the main window

window = tk.Tk()
window.attributes("-fullscreen", True)

# Optional: Add a keybinding to exit full screen mode
window.bind("<Escape>", lambda event: window.attributes("-fullscreen", False))
# Resize the window (you can adjust the size as needed)
window.geometry("1280x720")  # Set your desired window size

# Make the window non-resizable vertically (optional)
window.resizable(True, False)

# Set the title of the window
window.title("Attendance System")

# Position the window on the left side of the screen (x=0 is the left side)
window.geometry("1280x720+0+100")

# Verify and load the background image
background_image_path = r"bimage/background.jpg"
background_photo=None
# if os.path.exists(background_image_path):
#     try:
#         # Load and resize the image
#         background_image = Image.open(background_image_path)
#         # print(background_image)
#         background_image = background_image.resize((1280, 720), Image.Resampling.LANCZOS)  # High-quality resize
#
#         # Convert to Tkinter-compatible PhotoImage
#         background_photo = ImageTk.PhotoImage(background_image)
#         # print(background_photo)
#
#         # Display as the background
#         background_label = tk.Label(window, image=background_photo)
#         background_label.place(x=0, y=0, relwidth=1, relheight=1)
#
#     except Exception as e:
#         print(f"Error loading the image: {e}")
# else:
#     print(f"Background image not found at {background_image_path}")
if os.path.exists(background_image_path):
    try:
        # Load and resize the image
        background_image = Image.open(background_image_path)
        background_image = background_image.resize((1500, 900), Image.Resampling.LANCZOS)  # Resize image

        # Convert to Tkinter-compatible PhotoImage
        background_photo = ImageTk.PhotoImage(background_image)

        # Create a label and set the background image
        background_label = tk.Label(window, image=background_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Make the background cover the entire window
        # background_label.lift()
        background_label.pack(fill='both', expand=True)
        background_label.lower()
    except Exception as e:
        print(f"Error loading the image: {e}")
else:
    print(f"Background image not found at {background_image_path}")


# Create a Label to display the background image
# background_label = tk.Label(window, image=background_photo)
# background_label.place(x=0, y=0, relwidth=1, relheight=1)
# Create a Notebook (tabbed interface)
notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

# Create Frames for Tabs
left_frame = tk.Frame(notebook, bg="#e3f2fd")
right_frame = tk.Frame(notebook, bg="#e3f2fd")

# Add tabs to the notebook
notebook.add(left_frame, text="Main Panel")
notebook.add(right_frame, text="Admin Panel")

# Top Header (Title and Time)
header_frame = tk.Frame(window, bg="#00aeff")
header_frame.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)

header_label = tk.Label(header_frame, text="Face Recognition Based Attendance System",
                        fg="white", bg="#262523", width=55, height=2,
                        font=('times', 20, ' bold '))

header_label.pack(fill='both', expand=True)

# Time and Date Display
time_frame = tk.Frame(window, bg="#c4c6ce")
time_frame.place(relx=0.36, rely=0.09, relwidth=0.28, relheight=0.07)

time_label = tk.Label(time_frame, fg="orange", bg="#262523", font=('times', 16, 'bold'))
time_label.pack(expand=True)

# Function to Update Time
def update_time():
    current_time = time.strftime("%H:%M:%S")
    current_date = time.strftime("%d/%m/%Y")
    time_label.config(text=f"Date: {current_date} | Time: {current_time}")
    time_label.after(1000, update_time)

# Start the Time Update
update_time()

# Left Frame Content (Main Panel)
# track_attendance_button = tk.Button(left_frame, text="Take Attendance", fg="black", bg="yellow", width=35, height=1,
#                                     font=('times', 15, ' bold '), command=track_attendance)
# track_attendance_button.place(x=560, y=250)
#
# # Admin Panel Button
# admin_panel_button = tk.Button(left_frame, text="Admin Panel", fg="black", bg="green", width=35, height=1,
#                                font=('times', 15, ' bold '), command=admin_login)
# admin_panel_button.place(x=560, y=350)
#
# quit_button = tk.Button(left_frame, text="Quit", command=window.quit, fg="black", bg="red", width=35, height=1,
#                         font=('times', 15, ' bold '))
#
# quit_button.place(x=560, y=450)
track_attendance_button = tk.Button(window, text="Take Attendance", fg="black", bg="yellow", width=35, height=1,
                                    font=('times', 15, 'bold'),command=track_attendance)
track_attendance_button.place(x=560, y=250)
track_attendance_button.lift()  # Ensure the button is on top of the background

admin_panel_button = tk.Button(window, text="Admin Panel", fg="black", bg="green", width=35, height=1,
                               font=('times', 15, 'bold'),command=admin_login)
admin_panel_button.place(x=560, y=350)
admin_panel_button.lift()  # Ensure the button is on top of the background

quit_button = tk.Button(window, text="Quit", command=window.quit, fg="black", bg="red", width=35, height=1,
                        font=('times', 15, 'bold'))
quit_button.place(x=560, y=450)
quit_button.lift()  # Ensure the button is on top of the background

# Right Frame Content (Admin Panel)

# Function to create rounded corners for Entry
def create_rounded_entry(parent, x, y, width, height, placeholder):
    canvas = Canvas(parent, bg="#00aeff", bd=0, highlightthickness=0)
    canvas.place(x=x, y=y, width=width, height=height)

    # Draw rounded rectangle background
    radius = 10
    canvas.create_arc((0, 0, radius, radius), start=90, extent=90, fill="white", outline="")
    canvas.create_arc((width - radius, 0, width, radius), start=0, extent=90, fill="white", outline="")
    canvas.create_arc((0, height - radius, radius, height), start=180, extent=90, fill="white", outline="")
    canvas.create_arc((width - radius, height - radius, width, height), start=270, extent=90, fill="white", outline="")
    canvas.create_rectangle((radius, 0, width - radius, height), fill="white", outline="")
    canvas.create_rectangle((0, radius, width, height - radius), fill="white", outline="")

    # Create the actual Entry widget
    entry = ttk.Entry(parent, font=('times', 15, 'bold'), foreground="grey")
    entry.place(x=x + 10, y=y + 5, width=width - 20, height=height - 10)

    # Add placeholder text functionality
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, 'end')
            entry.config(foreground="black")

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground="grey")

    entry.insert(0, placeholder)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return entry

# Function to handle the 'Take Images' button click
def register_new_user():
    try:
        subprocess.Popen(["python", "face_fetching2.py"])  # Pass the name as an argument
        # messagebox.showinfo("Success", f"Started collecting faces for: {img_name}")
    except FileNotFoundError:
        messagebox.showerror("Error", "face_fetching2.py file not found. Please make sure it's in the same directory.")

# Button to trigger the image capture
take_images_button = tk.Button(right_frame, text="Register New User", fg="white", bg="orange", width=25, height=1,
                               font=('times', 15, ' bold '), command=register_new_user)
take_images_button.place(x=470, y=350)

def registered_students():
    try:
        # Run the script using subprocess
        subprocess.run(["python", "view_registered_students.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while executing view_registered_students.py: {e}")
    except FileNotFoundError:
        print("view_registered_students.py not found. Make sure it exists in the current directory.")

# Create the Save Profile button
registered_students = tk.Button(right_frame, text="veiw registered students", fg="white", bg="orange", width=25, height=1,
                                font=('times', 15, ' bold '), command=registered_students)

registered_students.place(x=470, y=420)
# Define the function to be executed when the button is clicked
def view_attendance():
    try:
        # Call the view_attendence.py script
        subprocess.run(["python", "view_attendance2.py"], check=True)
    except FileNotFoundError:
        print("The file 'view_attendence2.py' was not found. Please make sure it exists in the correct directory.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to run 'view_attendence2.py': {e}")
def get_monthly_reprt():
    try:
        # Call the view_attendence.py script
        subprocess.run(["python", "monthly_report.py"], check=True)
    except FileNotFoundError:
        print("The file 'monthly_report.py' was not found. Please make sure it exists in the correct directory.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to run 'monthly_report.py': {e}")

# Add the button to the right frame
view_attendance_button = tk.Button(
    right_frame,
    text="View Attendance",
    fg="white",
    bg="orange",
    width=25,
    height=1,
    font=('times', 15, 'bold'),
    command=view_attendance  # Make sure the function name matches
)

view_attendance_button.place(x=470, y=500)  # Adjust placement as needed
get_monthly_reprt_button = tk.Button(
    right_frame,
    text="Get Monthly Report",
    fg="white",
    bg="orange",
    width=25,
    height=1,
    font=('times', 15, 'bold'),
    command=get_monthly_reprt  # Make sure the function name matches
)

get_monthly_reprt_button.place(x=470, y=570)
# Function to switch to the Main Panel
def go_to_main_panel():
    notebook.select(left_frame)  # Switch to the Main Panel tab

# Back Button in the Admin Panel (Right Frame)
back_button = tk.Button(right_frame, text="Back", command=go_to_main_panel, fg="white", bg="#ba25fa", width=10, height=1,
                        font=('times', 15, ' bold '))
back_button.place(x=600, y=640)

# Start the Tkinter main loop
window.mainloop()

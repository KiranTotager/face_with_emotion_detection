import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import datetime
import os
import time


import re  # Import the regular expression module

# Function to validate the USN format (e.g., 4HG21CS000)
def validate_usn(usn):
    # Define the regex pattern for the USN (e.g., 4HG21CS000)
    pattern = r'^[1-9][A-Za-z]{2}\d{2}[A-Za-z]{2}\d{3}$'
    if re.match(pattern, usn):
        return True
    else:
        return False


# Function to handle database interaction
import mysql.connector
import re
from tkinter import messagebox  # Assuming tkinter is used for GUI

def generate_monthly_report(month, working_days, usn=None):
    conn = None  # Initialize conn to None
    try:
        # Validate month format
        if not re.match(r"^\d{4}-\d{2}$", month):
            raise ValueError("Month must be in the format 'YYYY-MM'")
        if working_days <= 0:
            raise ValueError("Working days must be a positive integer")

        # Establish MySQL connection
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendancesystem"
        )
        cursor = conn.cursor()

        # Generate the list of attendance tables for the given month
        table_prefix = f"attendance_{month[:4]}_{month[5:7]}" # Example: "attendance_2024_12"
        print(table_prefix)
        cursor.execute(f"SHOW TABLES LIKE '{table_prefix}%'")
        tables = cursor.fetchall()

        # Check if tables exist for the given month
        if not tables:
            messagebox.showwarning("No Data", f"No attendance data found for the month {month}.")
            return None

        # Construct the dynamic query to combine data from all daily attendance tables
        union_queries = []
        for table in tables:
            table_name = table[0]
            # Extract the date from the table name (assuming it's in the format 'attendance_YYYY_MM_DD')
            table_date = "_".join(table_name.split("_")[1:])  # Extract the 'YYYY_MM_DD' part
            full_date = table_date.replace("_", "-")  # Convert to full date format 'YYYY-MM-DD'

            sub_query = f"""
                SELECT 
                    u.usn AS student_id,
                    u.name AS student_name,
                    u.branch AS student_branch,
                    u.semester AS student_semester,
                    COUNT(a.usn) AS total_present,
                    {working_days} - COUNT(a.usn) AS total_absent,
                    MIN(a.erlier) AS earliest_attendance,
                    MAX(a.recent) AS latest_attendance,
                    (COUNT(a.usn) / {working_days}) * 100 AS attendance_percentage,
                    '{full_date}' AS attendance_date
                FROM 
                    {table_name} a
                LEFT JOIN 
                    users u 
                ON 
                    u.usn = a.usn
            """
            if usn:
                sub_query += f" WHERE u.usn = '{usn}'"  # Filter for specific USN
            sub_query += """
                GROUP BY 
                    u.usn, u.name, u.branch, u.semester
            """
            union_queries.append(sub_query)

        # Combine all the queries with UNION
        full_query = " UNION ALL ".join(union_queries)

        # Execute the combined query
        cursor.execute(full_query)
        report_data = cursor.fetchall()

        return report_data

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except ValueError as ve:
        print(f"Value Error: {ve}")
    finally:
        # Close the connection if it was successfully created
        if conn and conn.is_connected():
            conn.close()

# Function to display the results in a Treeview widget
# Function to handle form submission
# def on_submit():
#     month = month_combobox.get()  # Get selected month
#     usn = usn_entry.get().strip()  # Get the USN input from the user and remove extra spaces
#
#     # Validate that USN is provided and matches the required format
#     if not usn:
#         messagebox.showwarning("Input Error", "USN is required. Please enter a valid USN (e.g., 4HG21CS000).")
#         return
#     if not validate_usn(usn):
#         messagebox.showwarning("Input Error", "Invalid USN format. Please enter a valid USN (e.g., 4HG21CS000).")
#         return
#
#     try:
#         working_days = int(working_days_entry.get())  # Validate working days input
#         if not month:
#             messagebox.showwarning("Input Error", "Please select a valid month.")
#         else:
#             # Generate the report with the mandatory USN filter
#             report_data = generate_monthly_report(month, working_days, usn)
#
#             if report_data:
#                 # Display the generated report
#                 display_report(report_data,working_days)
#             else:
#                 messagebox.showwarning("No Data", "No data found for the selected month and USN.")
#     except ValueError:
#         messagebox.showwarning("Input Error", "Please enter a valid number of working days.")
def on_submit():
    month = month_combobox.get()  # Get selected month
    usn = usn_entry.get().strip()  # Get the USN input from the user and remove extra spaces

    # Validate that USN is provided and matches the required format
    if not usn:
        messagebox.showwarning("Input Error", "USN is required. Please enter a valid USN (e.g., 4HG21CS000).")
        return
    if not validate_usn(usn):
        messagebox.showwarning("Input Error", "Invalid USN format. Please enter a valid USN (e.g., 4HG21CS000).")
        return

    # Validate working days input
    try:
        working_days = int(working_days_entry.get())  # Try to convert the working days to an integer
        if working_days > 27:
            messagebox.showwarning("Input Error", "Working days must be less than or equal to 27.")
            return
    except ValueError:
        messagebox.showwarning("Input Error", "Please enter a valid number for working days.")
        return

    if not month:
        messagebox.showwarning("Input Error", "Please select a valid month.")
        return

    # Generate the report with the mandatory USN filter
    report_data = generate_monthly_report(month, working_days, usn)

    if report_data:
        # Display the generated report
        display_report(report_data, working_days)
    else:
        messagebox.showwarning("No Data", "No data found for the selected month and USN.")

def display_report(report_data, working_days):
    # Clear existing rows in the Treeview
    for row in tree.get_children():
        tree.delete(row)

    total_present = 0
    total_absent = 0
    attendance_percentage = 0

    # Ensure report_data contains data for at least one student
    if len(report_data) >= 1:
        for row in report_data:
            # Extract fields, including the new attendance_date
            usn, name, branch, semester, present, absent, earliest, latest, percentage, attendance_date = row
            total_present += present

            # Calculate total absent per student for the given working days
            total_absent = working_days - total_present
            attendance_percentage = (total_present / working_days) * 100 if working_days > 0 else 0

            # Update the labels with student details
            usn_label.config(text=f"USN: {usn}")
            name_label.config(text=f"Name: {name}")
            branch_label.config(text=f"Branch: {branch}")
            semester_label.config(text=f"Semester: {semester}")

            # Insert the student's attendance data into the Treeview (without USN, Name, Branch, Semester)
            tree.insert("", "end", values=( attendance_date,earliest, latest))

        # Update totals below the Treeview
        # Update individual total labels
        total_present_label.config(text=f"Total Present: {total_present}")
        total_absent_label.config(text=f"Total Absent: {total_absent}")
        average_attendance_label.config(text=f"Average Attendance Percentage: {attendance_percentage:.2f}%")
    else:
         # If no data is found for the specific student
        total_present_label.config(text="Total Present: N/A")
        total_absent_label.config(text="Total Absent: N/A")
        average_attendance_label.config(text="Average Attendance Percentage: N/A")

# def print_report():
#     # Create a temporary text file with the report data
#     try:
#         with open("monthly_report.txt", "w") as file:
#             file.write("Monthly Attendance Report\n")
#             file.write("=" * 30 + "\n\n")
#
#             # Write the selected month
#             selected_month = month_combobox.get()
#             file.write(f"Month: {selected_month}\n\n")
#
#             # Write the working days
#             working_days = working_days_entry.get()
#             file.write(f"Working Days: {working_days}\n\n")
#
#             # Write the USN if provided
#             usn = usn_entry.get()
#             if usn:
#                 file.write(f"Student USN: {usn}\n\n")
#
#             # Write the table headers
#             file.write("Student ID | Name | Branch | Semester | Earliest Attendance | Latest Attendance | Date\n")
#             file.write("-" * 80 + "\n")
#
#             # Write the Treeview data
#             for row in tree.get_children():
#                 values = tree.item(row, "values")
#                 file.write(" | ".join(values) + "\n")
#
#             # Totals
#             file.write("\n")
#             # file.write(total_label.cget("text") + "\n")
#             file.write("\nAttendance Summary:\n")
#             file.write(f"Total Present: {total_present_label.cget('text').split(': ')[1]}\n")
#             file.write(f"Total Absent: {total_absent_label.cget('text').split(': ')[1]}\n")
#             file.write(f"Average Attendance Percentage: {average_attendance_label.cget('text').split(': ')[1]}\n")
#     except Exception as e:
#
#         # Open the text file in the default text editor for printing
#         os.startfile("monthly_report.txt", "print")
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to print the report: {e}")
# def print_report():
#     try:
#         # Create a temporary text file with the report data
#         with open("monthly_report.txt", "w") as file:
#             file.write("Monthly Attendance Report\n")
#             file.write("=" * 30 + "\n\n")
#
#             # Write the selected month
#             selected_month = month_combobox.get()
#             file.write(f"Month: {selected_month}\n\n")
#
#             # Write the working days
#             working_days = working_days_entry.get()
#             file.write(f"Working Days: {working_days}\n\n")
#
#             # Write the USN if provided
#             usn = usn_entry.get()
#             if usn:
#                 file.write(f"Student USN: {usn}\n\n")
#
#             # Write the table headers
#             file.write("Student ID | Name | Branch | Semester | Earliest Attendance | Latest Attendance | Date\n")
#             file.write("-" * 80 + "\n")
#
#             # Write the Treeview data
#             for row in tree.get_children():
#                 values = tree.item(row, "values")
#                 file.write(" | ".join(values) + "\n")
#
#             # Write Attendance Summary
#             file.write("\nAttendance Summary:\n")
#             file.write(f"Total Present: {total_present_label.cget('text').split(': ')[1]}\n")
#             file.write(f"Total Absent: {total_absent_label.cget('text').split(': ')[1]}\n")
#             file.write(f"Average Attendance Percentage: {average_attendance_label.cget('text').split(': ')[1]}\n")
#
#         # Open the text file in the default text editor for printing
#         os.startfile("monthly_report.txt", "print")
#
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to print the report: {e}")

def print_report():
    try:
        # Create a temporary text file with the report data
        with open("monthly_report.txt", "w") as file:
            file.write("Government Engineering College, Mosalehosahalli\n")
            file.write("Monthly Attendance Report\n")
            file.write("=" * 50 + "\n\n")

            # Write the month, working days, and student details
            selected_month = month_combobox.get()
            working_days = working_days_entry.get()
            usn = usn_entry.get()  # USN from the entry widget
            name = name_label.cget("text")  # Name from the label (you might need an entry widget for name)
            branch = branch_label.cget("text")  # Branch from combobox
            semester = semester_label.cget("text")  # Semester from entry widget

            file.write(f"Month: {selected_month}\t\tWorking Days: {working_days}\n")
            file.write(f"USN: {usn}\t\t {name}  \t\t {branch}  \t\t {semester}\n\n")

            # Write the attendance summary
            total_present = total_present_label.cget('text').split(": ")[1]
            total_absent = total_absent_label.cget('text').split(": ")[1]
            attendance_percentage = average_attendance_label.cget('text').split(": ")[1]

            file.write(f"Total Present: {total_present}\tTotal Absent: {total_absent}\n")
            file.write(f"Attendance Percentage: {attendance_percentage}\n\n")

            # Write the attendance table headers with plain solid lines for boxes
            file.write("+------------------+--------------+--------------+\n")
            file.write("| Attendance Date  | Earliest     | Latest       |\n")
            file.write("+------------------+--------------+--------------+\n")

            # Write the attendance details for each date with boxes around the data
            for row in tree.get_children():
                values = tree.item(row, "values")
                date = values[0]
                earliest = values[1]
                latest = values[2]

                # Print each row with plain solid lines around the data
                file.write(f"| {date:<16} | {earliest:<12} | {latest:<12} |\n")
                file.write("+------------------+--------------+--------------+\n")

        # Open the text file in the default text editor for printing
        os.startfile("monthly_report.txt", "print")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to print the report: {e}")

def update_time():
    current_time = time.strftime("%H:%M:%S")
    current_date = time.strftime("%d/%m/%Y")
    time_label.config(text=f"Date: {current_date} | Time: {current_time}")
    time_label.after(1000, update_time)

root = tk.Tk()
root.title("Attendance System - Monthly Report")
root.geometry("1300x750")
root.configure(bg="#FFFFE0")
# Add a heading label (use grid instead of pack)
heading_label = tk.Label(root, text="Monthly Attendance Report", font=("Arial", 16, "bold"))
heading_label.grid(row=0, column=0, columnspan=4, pady=10, padx=10)

# Add time label (grid)
time_label = tk.Label(root, fg="orange", bg="#2d2d2d", font=('times', 14, 'bold'))
time_label.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
update_time()  # Call the function to update time

# Month selection, working days input, and USN input in a single row
month_label = tk.Label(root, text="Select Month:")
month_label.grid(row=2, column=0, padx=5, pady=2, sticky="e")

# Generate month options dynamically
current_year = datetime.datetime.now().year
# month_options = [f"{current_year}-{str(month).zfill(2)}" for month in range(1, 13)]
month_options = [f"{current_year-1}-{str(month).zfill(2)}" for month in range(1, 13)] + \
                [f"{current_year}-{str(month).zfill(2)}" for month in range(1, 13)]
month_combobox = ttk.Combobox(root, values=month_options, state="readonly", width=15)
month_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="w")

# Working days input
working_days_label = tk.Label(root, text="Working Days:")
working_days_label.grid(row=2, column=1, padx=10, pady=2, sticky="e")

working_days_entry = tk.Entry(root, width=10)
working_days_entry.grid(row=2, column=2, padx=10, pady=2, sticky="w")

# USN input
usn_label = tk.Label(root, text="Student USN:")
usn_label.grid(row=2, column=2, padx=10, pady=2, sticky="e")

usn_entry = tk.Entry(root, width=15)
usn_entry.grid(row=2, column=3, padx=5, pady=2, sticky="w")

# Frame to hold the labels
info_frame = tk.Frame(root)
info_frame.grid(row=5, column=0, rowspan=7, padx=10, pady=0, sticky="nw")  # Adjust grid settings

# Labels inside the frame
usn_label = tk.Label(info_frame, text="USN: ")
usn_label.pack(anchor="w", pady=1)

name_label = tk.Label(info_frame, text="Name: ")
name_label.pack(anchor="w", pady=1)

branch_label = tk.Label(info_frame, text="Branch: ")
branch_label.pack(anchor="w", pady=1)

semester_label = tk.Label(info_frame, text="Semester: ")
semester_label.pack(anchor="w", pady=1)

# Total Present
total_present_label = tk.Label(info_frame, text="Total Present: 0")
total_present_label.pack(anchor="w", pady=2)

# Total Absent
total_absent_label = tk.Label(info_frame, text="Total Absent: 0")
total_absent_label.pack(anchor="w", pady=2)

# Average Attendance Percentage
average_attendance_label = tk.Label(info_frame, text="Average Attendance Percentage: 0.00%")
average_attendance_label.pack(anchor="w", pady=2)

# Submit button (adjusted positioning)
submit_button = tk.Button(root, text="Generate Report", bg="#A8D5BA", fg="black", command=on_submit)
submit_button.grid(row=6, column=0, padx=5, pady=2, sticky="e")

# Print button (adjusted positioning)
# print_button = tk.Button(root, text="Print Report", command=print_report)
print_button = tk.Button(root, text="Print Report", bg="#FFDAB9", fg="black", command=print_report)

print_button.grid(row=6, column=1, padx=5, pady=2, sticky="w")
# # Position the Treeview (adjusted grid row, column, and span)
# tree.grid(row=6, column=2, columnspan=2, padx=30, pady=10, sticky="nsew")
# Create a style for the Treeview
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="#333333", background="#D3D3D3")
style.configure("Treeview", font=("Arial", 9))  # Optional: Set font for data rows

# Treeview setup
columns = ("Date", "Earliest Attendance", "Latest Attendance")
tree = ttk.Treeview(root, columns=columns, show="headings", height=5)  # Adjust height

# Set specific column widths
tree.column("Date", width=120, anchor="center")
tree.column("Earliest Attendance", width=180, anchor="center")
tree.column("Latest Attendance", width=180, anchor="center")

# Set column headings without the style option
tree.heading("Date", text="Date", anchor="center")
tree.heading("Earliest Attendance", text="Earliest Attendance", anchor="center")
tree.heading("Latest Attendance", text="Latest Attendance", anchor="center")

# Position the Treeview (adjust grid row, column, and span)
tree.grid(row=6, column=2, columnspan=2, padx=30, pady=10, sticky="nsew")  # Adjust column span and position


# Configure grid weights for responsiveness
root.grid_columnconfigure(0, weight=0)  # No stretching for the label column
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_rowconfigure(6, weight=1)

# Start the GUI loop
root.mainloop()

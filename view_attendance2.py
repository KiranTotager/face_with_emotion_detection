import tkinter as tk
from tkinter import ttk
import sqlite3
from tkcalendar import DateEntry
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime
# Main Window Setup
window = tk.Tk()
window.geometry("1280x720")
window.resizable(False, False)
window.title("Attendance System")
window.configure(background='#e368cc')

# Header Frame
header_frame = tk.Frame(window, bg="#a11587")
header_frame.place(relx=0.0, rely=0.0, relwidth=1, relheight=0.1)

header_label = tk.Label(
    header_frame,
    text="Face Recognition Based Attendance System",
    fg="white",
    bg="#262523",
    font=('times', 20, ' bold ')
)
header_label.pack(fill='both', expand=True)

# Time and Date Display
time_frame = tk.Frame(window, bg="#c4c6ce")
time_frame.place(relx=0.36, rely=0.09, relwidth=0.28, relheight=0.07)

time_label = tk.Label(time_frame, fg="orange", bg="#262523", font=('times', 16, 'bold'))
time_label.pack(expand=True)


def update_time():
    current_time = time.strftime("%H:%M:%S")
    current_date = time.strftime("%d/%m/%Y")
    time_label.config(text=f"Date: {current_date} | Time: {current_time}")
    time_label.after(1000, update_time)


update_time()

# Left Frame for Attendance Records
left_frame = tk.Frame(window, bg="#c9adc4", bd=2, relief="groove")
left_frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.75)

# Title
title_label = tk.Label(left_frame, text="Attendance Records", font=("Courier New", 26, "bold")
, bg="#c9adc4", fg="#333333")
title_label.place(x=400, y=10)
style = ttk.Style(window)
style.configure("Treeview",
                rowheight=25,
                bordercolor="black",
                borderwidth=1)
style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

style.layout("Treeview", [
    ("Treeview.treearea", {"sticky": "nswe"})  # Removes the borders of the treeview
])

branch_mapping = {
    "Computer Science and Engineering": "CS",
    "Civil Engineering": "CV",
    "Mechanical Engineering": "ME",
    "Electronics and Communication Engineering": "ECE",
    "Electrical and Electronics Engineering": "EEE"
}

treeview = ttk.Treeview(left_frame, height=13, columns=('USN', 'Name', 'Semester', 'erlier','recent'))

# Configuring column widths and alignment
treeview.column('#0', width=50, anchor='center')  # Default column for IDs
treeview.column('USN', width=125, anchor='center')
treeview.column('Name', width=125, anchor='center')  # Added column for USN
treeview.column('Semester', width=50, anchor='center')
treeview.column('erlier', width=100, anchor='center')
treeview.column('recent', width=100, anchor='center')

# Setting column headings
treeview.heading('#0', text='ID')
treeview.heading('USN', text='USN')
treeview.heading('Name', text='Name')  # Heading for the USN column
treeview.heading('Semester', text='Semester')
treeview.heading('erlier', text='Earlier')
treeview.heading('recent', text='Recent')
treeview.place(x=200, y=100, width=740, height=300)

# Scrollbar for Treeview
scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=treeview.yview)
scrollbar.place(x=940, y=100, height=300)
treeview.configure(yscrollcommand=scrollbar.set)

# Date Picker and Populate Function

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "attendancesystem"
}


print("db_config:", db_config)
print("Type of db_config:", type(db_config))


def populate_treeview(treeview, db_config, branch_code=None, selected_date=None):
    """
    Populate the Treeview with attendance data filtered by branch and/or date.

    Args:
        treeview: The Treeview widget to populate.
        db_config (dict): Database connection configuration.
        branch_code (str, optional): The branch code to filter data.
        selected_date (str, optional): The selected date to filter data.
    """
    # Clear the Treeview first
    for row in treeview.get_children():
        treeview.delete(row)
    print(f"Selected date: {selected_date}")

    # Format the selected_date into yyyy_mm_dd format
    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            table_date = date_obj.strftime("%Y_%m_%d")  # Create the table name suffix
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
    else:
        print("No date selected")
        return

    # Build the dynamic table name
    table_name = f"attendance_{table_date}"

    # Build the WHERE clause based on filters
    where_clauses = []
    if branch_code:
        where_clauses.append(f"usn LIKE '%{branch_code}%'")

    where_clause = " AND ".join(where_clauses)

    # Construct the query using the dynamic table name
    query = f"SELECT usn, name, sem, erlier,recent FROM {table_name}"
    if where_clause:
        query += f" WHERE {where_clause}"

    print(f"Executing query: {query}")  # Debugging line

    # Connect to the MySQL database
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        if conn.is_connected():
            cursor = conn.cursor()

            try:
                cursor.execute(query)  # Execute the correctly constructed query
                records = cursor.fetchall()
                id=0
                # Populate the Treeview with fetched data
                for record in records:
                    treeview.insert('', 'end', text=id, values=(record[0], record[1], record[2], record[3],record[4]))
                    id=id+1

            except Error as e:
                print(f"Error fetching data: {e}")
            finally:
                cursor.close()

    except Error as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
def on_date_change(event):
    # selected_date = date_entry.get_date().strftime("%Y-%m-%d")
    selected_date = date_entry.get_date().strftime("%Y-%m-%d")
    populate_treeview(treeview,db_config ,None,selected_date)

date_label = tk.Label(left_frame, text="Select Date:", font=("Helvetica", 12, "bold"), bg="#c9adc4", fg="#333333")
date_label.place(x=800, y=70)

date_entry = DateEntry(left_frame, width=12, background="#007BFF", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd")
date_entry.place(x=900, y=70)
date_entry.bind("<<DateEntrySelected>>", on_date_change)

branch_label = tk.Label(left_frame, text="Select Branch:", font=("Helvetica", 12, "bold"), bg="#c9adc4", fg="#333333")
branch_label.place(x=370, y=70)

def on_branch_select(event, treeview, db_config, branch_combobox):
    """
    Event handler for when a branch is selected.

    Args:
        event: The event object.
        treeview: The Treeview widget to update.
        db_config (dict): Database connection configuration.
        branch_combobox: The Combobox widget for branch selection.
    """
    selected_branch_full = branch_combobox.get()  # Get selected branch full form
    branch_code = branch_mapping.get(selected_branch_full, None)  # Get corresponding branch code
    if branch_code:
        populate_treeview(treeview, db_config,branch_code )

# branch_combobox.bind("<<ComboboxSelected>>", on_branch_change)
branch_combobox = ttk.Combobox(window, values=list(branch_mapping.keys()), state='readonly')
branch_combobox.set("Select Branch")
branch_combobox.bind('<<ComboboxSelected>>', lambda e: on_branch_select(e, treeview, db_config, branch_combobox))
branch_combobox.place(x=550, y=180)
# Footer Refresh Button

style = ttk.Style()
style.configure("Refresh.TButton", font=('times', 15, 'bold'), background="#4CAF50", foreground="black")
style.configure("Close.TButton", font=('times', 15, 'bold'), background="#ba25fa", foreground="black")

# Refresh Button with the new style (green background)
refresh_button = ttk.Button(left_frame, text="Refresh", command=lambda: on_date_change(None), style="Refresh.TButton")
refresh_button.place(x=400, y=460)

# Close Button with the defined style (purple background)
close_button = ttk.Button(left_frame, text="Close", command=window.destroy, style="Close.TButton")
close_button.place(x=600, y=460)

# Mainloop
window.mainloop()

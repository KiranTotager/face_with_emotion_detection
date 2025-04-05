import tkinter as tk
from tkinter import messagebox

def setup_admin_login(window, notebook):
    def verify_admin(username, password, login_window):
        admin_username = "kiran"
        admin_password = "kiran123"

        if username == admin_username and password == admin_password:
            login_window.destroy()
            notebook.select(1)  # Switch to the Admin Panel tab
        else:
            messagebox.showerror("Invalid credentials", "The username or password is incorrect.")

    def admin_login():
        login_window = tk.Toplevel(window)
        login_window.geometry("400x300")
        login_window.title("Admin Login")
        login_window.config(bg="#00aeff")

        tk.Label(login_window, text="Admin Login", font=('times', 18, 'bold'), bg="#00aeff", fg="white").pack(pady=20)

        username_label = tk.Label(login_window, text="Username", font=('times', 14), bg="#00aeff", fg="white")
        username_label.pack(pady=5)
        username_entry = tk.Entry(login_window, font=('times', 14))
        username_entry.pack(pady=5)

        password_label = tk.Label(login_window, text="Password", font=('times', 14), bg="#00aeff", fg="white")
        password_label.pack(pady=5)
        password_entry = tk.Entry(login_window, show="*", font=('times', 14))
        password_entry.pack(pady=5)

        login_button = tk.Button(login_window, text="Login", font=('times', 16, 'bold'),
                                 command=lambda: verify_admin(username_entry.get(), password_entry.get(), login_window),
                                 bg="#4CAF50", fg="white", relief="flat", width=15)
        login_button.pack(pady=20)

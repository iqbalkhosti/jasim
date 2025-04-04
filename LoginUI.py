# login_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import csv
from account_creation_backend import register_user

class LoginUI:
    def __init__(self, root, success_callback):
        self.root = root
        self.success_callback = success_callback
        self._setup_window()
        self._create_widgets()
        
    def _setup_window(self):
        self.root.title("Vehicle Catalog System - Login")
        self.root.geometry("500x500")
        self.root.configure(bg="#F0F2F5")
        self.root.resizable(False, False)
        
    def _create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg="#F0F2F5")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Login Card
        login_card = tk.Frame(self.main_frame, bg="white", padx=30, pady=30, 
                            bd=0, highlightthickness=0)
        login_card.pack(pady=20, ipadx=20, ipady=10)

        # Title
        title = tk.Label(login_card, text="Welcome Back!", 
                       font=("Arial", 20, "bold"), bg="white")
        title.pack(pady=(0, 20))

        # Login Form
        form_frame = tk.Frame(login_card, bg="white")
        form_frame.pack()

        # Username
        self.username_label = ttk.Label(form_frame, text="Username:", 
                                      font=("Arial", 10), background="white")
        self.username_label.grid(row=0, column=0, pady=5, sticky="w")
        self.username_entry = ttk.Entry(form_frame, width=25)
        self.username_entry.grid(row=1, column=0, pady=5)

        # Password
        self.password_label = ttk.Label(form_frame, text="Password:", 
                                      font=("Arial", 10), background="white")
        self.password_label.grid(row=2, column=0, pady=5, sticky="w")
        self.password_entry = ttk.Entry(form_frame, show="•", width=25)
        self.password_entry.grid(row=3, column=0, pady=5)

        # Error Message
        self.error_label = ttk.Label(form_frame, text="", 
                                   foreground="red", background="white")
        self.error_label.grid(row=4, column=0, pady=5)

        # Login Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, pady=15)

        ttk.Button(button_frame, text="User Login", 
                  command=self._authenticate_user, width=12).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Admin Login", 
                  command=self._authenticate_admin, width=12).grid(row=0, column=1, padx=5)

        # Secondary Options
        options_frame = ttk.Frame(form_frame)
        options_frame.grid(row=6, column=0, pady=10)

        ttk.Button(options_frame, text="Create Account", 
                  command=self._show_signup, width=15).grid(row=0, column=0, padx=5)
        ttk.Button(options_frame, text="Continue as Guest", 
                  command=self._guest_login, width=18).grid(row=0, column=1, padx=5)

    def _clear_error(self):
        self.error_label.config(text="")

    def _show_error(self, message):
        self.error_label.config(text=message)
        self.root.after(3000, self._clear_error)

    def _authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self._show_error("Please fill in all fields")
            return

        try:
            with open("users.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0] == username and row[2] == password:
                        self._cleanup()
                        self.success_callback('user', username)
                        return
                self._show_error("Invalid username or password")
        except FileNotFoundError:
            self._show_error("No registered users found")

    def _authenticate_admin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            with open("admins.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0] == username and row[2] == password:
                        self._cleanup()
                        self.success_callback('admin', username)
                        return
                self._show_error("Invalid admin credentials")
        except FileNotFoundError:
            self._show_error("Admin database not found")

    def _guest_login(self):
        self._cleanup()
        self.success_callback('guest', None)

    def _show_signup(self):
        signup_window = tk.Toplevel(self.root)
        signup_window.title("Create Account")
        signup_window.geometry("400x400")
        signup_window.configure(bg="#F0F2F5")
        signup_window.grab_set()

        # Signup Form
        form_frame = tk.Frame(signup_window, bg="#F0F2F5", padx=20, pady=20)
        form_frame.pack(expand=True, fill="both")

        tk.Label(form_frame, text="Create New Account", 
                font=("Arial", 16, "bold"), bg="#F0F2F5").pack(pady=10)

        entries = {}
        fields = ["Username:", "Email:", "Password:"]
        for idx, field in enumerate(fields):
            tk.Label(form_frame, text=field, bg="#F0F2F5").pack(pady=5)
            entry = ttk.Entry(form_frame, width=25)
            entry.pack(pady=5)
            entries[field.replace(":", "").lower()] = entry

        error_label = tk.Label(form_frame, text="", fg="red", bg="#F0F2F5")
        error_label.pack(pady=5)

        def submit():
            username = entries['username'].get()
            email = entries['email'].get()
            password = entries['password'].get()

            if not all([username, email, password]):
                error_label.config(text="All fields are required")
                return

            try:
                with open("users.csv", "r") as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row and row[0] == username:
                            error_label.config(text="Username already exists")
                            return
            except FileNotFoundError:
                pass

            register_user(username, email, password, "user")
            messagebox.showinfo("Success", "Account created successfully!")
            signup_window.destroy()

        ttk.Button(form_frame, text="Create Account", 
                  command=submit, width=20).pack(pady=15)

    def _cleanup(self):
        self.main_frame.destroy()
        self.root.title("Vehicle Catalog System")
        self.root.geometry("900x600")

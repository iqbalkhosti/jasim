import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from iteration_01_main import add_car, update_car, remove_car, save_catalog, if_exist, catalog, categories

class CatalogApp:
    def __init__(self, root):
        # Initialize the application window with a title, size, and background color
        # Calls the login screen method to start the application
        self.root = root
        self.root.title("Catalog System")
        self.root.geometry("500x500")
        self.root.configure(bg="#f0f8ff")
        self.login_screen()

    def login_screen(self):
        # Creates the login screen with username and password input fields
        # Displays an error message if login fails
        self.clear_window()
        frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Login", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        username_entry, password_entry = tk.Entry(frame), tk.Entry(frame, show="*")

        for label, entry in zip(["Username:", "Password:"], [username_entry, password_entry]):
            tk.Label(frame, text=label, bg="white").pack()
            entry.pack()

        tk.Button(
            frame,
            text="Login",
            command=lambda: self.main_menu() if username_entry.get() == "" and password_entry.get() == ""
            else messagebox.showerror("Login Failed", "Invalid username or password"),
            bg="#4682B4", fg="white"
        ).pack(pady=10)

    def main_menu(self):
        # Displays the main menu with options to search, display catalog, add, update, or remove items
        # Includes a search bar and a dropdown menu for selecting actions
        self.clear_window()
        frame = tk.Frame(self.root, bg="#f0f8ff")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        search_frame = tk.Frame(frame, bg="white", padx=10, pady=5, relief=tk.RIDGE, bd=2)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Search:", bg="white").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.bind("<Return>", lambda event: self.search())
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Go", command=self.search, bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)

        self.selected_option = tk.StringVar(value="Select Option")
        dropdown = ttk.Combobox(frame, textvariable=self.selected_option,
                                values=["Display Catalog", "View Item Details", "Add Entry", "Update Entry", "Remove Entry", "Save Catalog", "Exit"],
                                state="readonly")
        dropdown.pack(pady=10)
        dropdown.bind("<<ComboboxSelected>>", self.handle_dropdown_selection)

    def search(self):
        # Searches the catalog based on user input and displays matching results
        # term = self.search_entry.get().strip().lower()
        # # results = [item for item in catalog if term in item['Make'].lower() or term in item['Model'].lower()] if term else catalog
        # results = [item for item in catalog if any(term in str(item[category]).lower() for category in categories)] if term else catalog
        terms = self.search_entry.get().strip().lower().split()
        results = [item for item in catalog if all(any(term in str(item[category]).lower() for category in categories) for term in terms)] if terms else catalog
        self.display_results(results)

    def handle_dropdown_selection(self, event):
        # Executes the selected action from the dropdown menu
        actions = {
            "Display Catalog": lambda: self.display_results(catalog),
            "View Item Details": self.view_item,
            "Add Entry": self.add_item,
            "Update Entry": self.update_item,
            "Remove Entry": self.remove_item,
            "Save Catalog": save_catalog,
            "Exit": self.on_closing
        }
        action = actions.get(self.selected_option.get())
        if action:
            action()

    def display_results(self, results):
        # Displays search results in the form of clickable buttons
        self.clear_window()
        frame = tk.Frame(self.root, bg="#f0f8ff")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame, text="Search Results:", font=("Arial", 14, "bold"), bg="#f0f8ff").pack()

        for item in results:
            tk.Button(frame, text=f"{item['ID']}: {item['Make']} {item['Model']}",
                      command=lambda i=item: self.display_item_details(i),
                      bg="white", relief=tk.RIDGE).pack(fill=tk.X, padx=10, pady=2)

        tk.Button(frame, text="Back", command=self.main_menu, bg="#4682B4", fg="white").pack(pady=10)

    def display_item_details(self, item):
        # Displays detailed information about a selected item
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        self.clear_window()
        frame = tk.Frame(self.root, bg="#f0f8ff")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for key, value in item.items():
            tk.Label(frame, text=f"{key}: {value}", font=("Arial", 12), bg="#f0f8ff").pack()
        
        button_frame = tk.Frame(frame, bg="#f0f8ff")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Update", command=lambda: self.update_item(item.get('ID')), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove", command=lambda: self.remove_item(item.get('ID')), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Back", command=self.main_menu, bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)

    def view_item(self):
        item_id = simpledialog.askstring("View Item", "Enter item ID:")
        item = next((i for i in catalog if i['ID'] == item_id), None)
        self.display_item_details(item)

    def add_item(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Add Item", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        labels = [label + ":" for label in categories[1:]]
        entries = [tk.Entry(frame) for _ in categories[1:]]

        for label, entry in zip(labels, entries):
            tk.Label(frame, text=label, bg="white").pack()
            entry.pack()

        tk.Button(
            frame,
            text="Add",
            command= lambda: self.send_info(entries),
            bg="#4682B4", fg="white"
        ).pack(pady=10)
        tk.Button(frame, text="Back", command=self.main_menu, bg="#4682B4", fg="white").pack(pady=10)
    
    def update_item(self, ID=None):
        if ID is None:
            ID = simpledialog.askstring("Update Item", "Enter item ID to update:")
        item = next((i for i in catalog if i['ID'] == ID), None)
        if not item:
            messagebox.showerror("Error", "Item not found")
            return
        self.clear_window()
        frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Update Item", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        labels = [label + ":" for label in categories[1:]]
        entries = [tk.Entry(frame) for _ in categories[1:]]

        for label, entry in zip(labels, entries):
            tk.Label(frame, text=label, bg="white").pack()
            entry.insert(0, item.get(label.strip(": ")))
            entry.pack()

        tk.Button(
            frame,
            text="Update",
            command= lambda: self.send_info(entries, ID),
            bg="#4682B4", fg="white"
        ).pack(pady=10)
        tk.Button(frame, text="Back", command=self.main_menu, bg="#4682B4", fg="white").pack(pady=10)

    def send_info(self, entries, ID=None):
        if ID:
            car_info = dict({"ID": ID}, **{key: entry.get() for key, entry in zip(categories[1:], entries)})
        else:
            # If no previous ID is provided, generate a new one based on the last element in the catalog
            car_info = dict({"ID": str(int(catalog[-1].get("ID"))+1)}, **{key: entry.get() for key, entry in zip(categories[1:], entries)})
        print(car_info)
        if car_info["Model"] and car_info["Year"].isdigit():
            if ID:
                update_car(car_info)
            else:
                add_car(car_info)
            self.main_menu() 
        else:
            # Maybe better error message for what is wrong specifics?
            messagebox.showerror("Error", "Either missing Model or incorrect Year")

    def remove_item(self, ID=None):
        if not ID:
            ID = simpledialog.askstring("Remove Item", "Enter item ID to remove:")
        if ID:
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove this item?")
            if confirm:
                remove_car(ID)
                messagebox.showinfo("Success", "Car removed successfully")
        self.main_menu()

    def on_closing(self):
        if messagebox.askyesno("Save Catalog", "Would you like to save the catalog before exiting?"):
            save_catalog()
        self.root.destroy()

    def clear_window(self):
        # Clears all widgets from the window before updating the UI
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    CatalogApp(root)
    root.mainloop()

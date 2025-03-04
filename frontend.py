import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from iteration_01_main import add_car, update_car, remove_car, if_exist, catalog, categories

class CatalogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Catalog System")
        self.root.geometry("500x500")
        self.root.configure(bg="#f0f8ff")
        self.login_screen()

    def login_screen(self):
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
        self.clear_window()
        frame = tk.Frame(self.root, bg="#f0f8ff")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        search_frame = tk.Frame(frame, bg="white", padx=10, pady=5, relief=tk.RIDGE, bd=2)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Search:", bg="white").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Go", command=self.search, bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)

        self.selected_option = tk.StringVar(value="Select Option")
        dropdown = ttk.Combobox(frame, textvariable=self.selected_option,
                                values=["Display Catalog", "View Item Details", "Add Entry", "Update Entry", "Remove Entry", "Exit"],
                                state="readonly")
        dropdown.pack(pady=10)
        dropdown.bind("<<ComboboxSelected>>", self.handle_dropdown_selection)

    def search(self):
        term = self.search_entry.get().strip().lower()
        results = [item for item in catalog if term in item['Make'].lower() or term in item['Model'].lower()] if term else catalog
        self.display_results(results)

    def handle_dropdown_selection(self, event):
        actions = {
            "Display Catalog": lambda: self.display_results(catalog),
            "View Item Details": self.view_item,
            "Add Entry": self.add_item,
            "Update Entry": self.update_item,
            "Remove Entry": self.remove_item,
            "Exit": self.root.quit
        }
        actions.get(self.selected_option.get(), lambda: None)()

    def display_results(self, results):
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
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        self.clear_window()
        frame = tk.Frame(self.root, bg="#f0f8ff")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for key, value in item.items():
            tk.Label(frame, text=f"{key}: {value}", font=("Arial", 12), bg="#f0f8ff").pack()

        tk.Button(frame, text="Back", command=self.main_menu, bg="#4682B4", fg="white").pack(pady=10)

    def view_item(self):
        item_id = simpledialog.askstring("View Item", "Enter item ID:")
        item = next((i for i in catalog if i['ID'] == item_id), None)
        self.display_item_details(item)

    def add_item(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Add Item", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        username_entry, password_entry = tk.Entry(frame), tk.Entry(frame)
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
    
    def update_item(self):
        item_id = simpledialog.askstring("Update Item", "Enter item ID to update:")
        item = next((i for i in catalog if i['ID'] == item_id), None)
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
            command= lambda: self.send_info(entries, item_id),
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

    def remove_item(self):
        item_id = simpledialog.askstring("Remove Item", "Enter item ID to remove:")
        if item_id:
            remove_car(item_id)
            messagebox.showinfo("Success", "Car removed successfully")
        self.main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    CatalogApp(root)
    root.mainloop()

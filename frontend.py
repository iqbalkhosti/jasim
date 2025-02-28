import tkinter as tk
from tkinter import messagebox, simpledialog
from iteration_01_main import add_car, remove_car, if_exist, find_match_items, show_specif_car, catalog

class CatalogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Catalog System")
        self.root.geometry("500x500")
        self.login_screen()

    def login_screen(self):
        self.clear_window()
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Login", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(frame, text="Username:").pack()
        username_entry = tk.Entry(frame)
        username_entry.pack()
        
        tk.Label(frame, text="Password:").pack()
        password_entry = tk.Entry(frame, show="*")
        password_entry.pack()

        def attempt_login():
            if username_entry.get() == "username" and password_entry.get() == "password":
                self.main_menu()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

        tk.Button(frame, text="Login", command=attempt_login).pack(pady=10)
    
    def main_menu(self):
        self.clear_window()
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        buttons = [
            ("Display Catalog", lambda: self.display_results(catalog)),
            ("View Item Details", self.view_item),
            ("Add Entry", self.add_item),
            ("Remove Entry", self.remove_item),
            ("Exit", self.root.quit)
        ]
        
        for text, command in buttons:
            tk.Button(frame, text=text, command=command, font=("Arial", 12), width=30).pack(pady=5)
    
    def display_results(self, results):
        self.clear_window()
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Search Results:", font=("Arial", 14, "bold")).pack()
        
        for item in results:
            tk.Button(frame, text=f"{item['ID']}: {item['Make']} {item['Model']}",
                      command=lambda i=item: self.display_item_details(i)).pack(fill=tk.X, padx=10, pady=2)
        
        tk.Button(frame, text="Back", command=self.main_menu).pack(pady=10)
    
    def display_item_details(self, item):
        self.clear_window()
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for key, value in item.items():
            tk.Label(frame, text=f"{key}: {value}", font=("Arial", 12)).pack()
        
        tk.Button(frame, text="Back", command=self.main_menu).pack(pady=10)
    
    def view_item(self):
        item_id = simpledialog.askstring("View Item", "Enter item ID:")
        item = next((i for i in catalog if i['ID'] == item_id), None)
        if item:
            self.display_item_details(item)
        else:
            messagebox.showerror("Error", "Item not found")
    
    def add_item(self):
        car_info = {key: simpledialog.askstring("Add Car", f"Enter Car {key}:") for key in ["ID", "Make", "Model", "Year", "Color"]}
        if not if_exist(car_info["ID"]):
            add_car(car_info)
            messagebox.showinfo("Success", "Car added successfully")
        else:
            messagebox.showerror("Error", "Car ID already exists")
        self.main_menu()
    
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
    app = CatalogApp(root)
    root.mainloop()
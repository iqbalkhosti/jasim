import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
##from tkVideoPlayer import TkinterVideo
from database_backend import Database

class CatalogApp:
    text = ""
    DB = Database()
    def __init__(self, root):
        # Initialize the application window with a title, size, and background color
        # Calls the login screen method to start the application
        self.root = root
        self.root.title("Catalog System")
        self.root.geometry("800x600")  # Increased size to match mockup
        self.root.configure(bg="white")
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
        # Includes a search bar and dropdown menus for filtering
        self.clear_window()
        
        # Main container
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top bar for search and menu
        top_frame = tk.Frame(main_frame, bg="white", bd=1, relief=tk.SOLID)
        top_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Search bar that spans most of the top
        search_frame = tk.Frame(top_frame, bg="white")
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        self.search_entry = tk.Entry(search_frame, width=80, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Search")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "Search" else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "Search") if not self.search_entry.get() else None)
        self.search_entry.bind("<Return>", lambda e: self.search(True))
        
        # Menu button at top right
        menu_frame = tk.Frame(top_frame, bg="white")
        menu_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Using a button with symbol for the dropdown menu
        self.menu_button = tk.Button(menu_frame, text="≡", font=("Arial", 16), bg="white", bd=1, command=self.show_menu_dropdown)
        self.menu_button.pack(side=tk.RIGHT)
        
        # Content area - split into left (filters) and right (results)
        self.content_frame = tk.Frame(main_frame, bg="white")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - filter dropdowns
        filter_frame = tk.Frame(self.content_frame, bg="white", width=240)
        filter_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        filter_frame.pack_propagate(False)  # Maintain width
        
        # Creates as many dropdowns as there are categories
        for key in self.DB.get_categories():
            # FOR NOW, I've hard coded removing dropdowns for VIDEO and ID.
            # Obviously you wouldn't sort by these, but this is sort of a hotfix
            # Open to better fixes
            if(key != "ID" and key!= "Video"):
                self.create_filter_dropdown(filter_frame, key)
        
        # Right side - results grid
        self.results_frame = tk.Frame(self.content_frame, bg="white")
        self.results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize terms list for filters
        self.terms = []
        
        # Load initial catalog display
        self.display_catalog_grid(self.DB.get_car_catalog())

    def create_filter_dropdown(self, parent, title):
        # Create expandable dropdown filter menu
        frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.X, pady=5)
        
        # Header with expand/collapse button
        header_frame = tk.Frame(frame, bg="white")
        header_frame.pack(fill=tk.X)
        
        # Keep track of dropdown state
        is_expanded = tk.BooleanVar(value=False)
        
        def toggle_dropdown():
            is_expanded.set(not is_expanded.get())
            if is_expanded.get():
                content_frame.pack(fill=tk.X, pady=5)
                toggle_button.config(text="v")
            else:
                content_frame.pack_forget()
                toggle_button.config(text=">")
        
        # Header with title and toggle button
        tk.Label(header_frame, text=title, font=("Arial", 12, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
        toggle_button = tk.Button(header_frame, text=">", bg="white", bd=0, command=toggle_dropdown)
        toggle_button.pack(side=tk.RIGHT, padx=5)
        
        # Content frame for checkboxes
        content_frame = tk.Frame(frame, bg="white", padx=10)
        
        # Add checkboxes for each fitler in category
        filter_vars = []
        filter_list = list({d[title]for d in self.DB.get_car_catalog()}) # List of all unique filters per category
        for filter in filter_list:
            var = tk.BooleanVar()
            filter_vars.append(var)
            cb = tk.Checkbutton(content_frame, text=filter, variable=var, bg="white",
                                command=lambda: self.apply_filters(title, filter_list))
            cb.pack(anchor="w")
        
        # Store references for later use
        if not hasattr(self, 'filter_checkboxes'):
            self.filter_checkboxes = {}
        self.filter_checkboxes[title] = filter_vars

    def apply_filters(self, title, filter_list):
        # Apply selected filters to the search
        self.text = ""
        if hasattr(self, 'filter_checkboxes'):
            for title, checkbox_vars in self.filter_checkboxes.items():
                for i, var in enumerate(checkbox_vars):
                    if var.get():
                        if(filter_list[i] not in self.text):
                            self.text += (filter_list[i]) + " "
        self.search()
    
    def show_menu_dropdown(self):
        # Create popup menu at the button location
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Display Catalog", command=lambda: self.display_results(self.DB.get_car_catalog()))
        menu.add_command(label="View Item Details", command=self.view_item)
        menu.add_command(label="Add Entry", command=self.add_item)
        menu.add_command(label="Update Entry", command=self.update_item)
        menu.add_command(label="Remove Entry", command=self.remove_item)
        menu.add_command(label="Save Catalog", command=self.on_save)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.on_closing)
        
        # Position menu below the button
        x = self.menu_button.winfo_rootx()
        y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        menu.tk_popup(x, y)

    def search(self, from_menu=False):
        if from_menu:
            self.text = self.search_entry.get()
            if self.text == "Search":
                self.text = ""
        self.display_results(self.DB.search(self.text))

    def display_catalog_grid(self, results):
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not results:
            tk.Label(self.results_frame, text="No results found", bg="white").pack()
            return
            
        # Create grid layout
        row_frame = None
        for idx, item in enumerate(results):
            # Create a new row for every 3 items
            if idx % 3 == 0:
                row_frame = tk.Frame(self.results_frame, bg="white")
                row_frame.pack(fill=tk.X, pady=5)
                
            # Create card for each item
            card = tk.Frame(row_frame, bd=1, relief=tk.SOLID, bg="white", width=200, height=250)
            card.pack(side=tk.LEFT, padx=5, fill=tk.BOTH)
            card.pack_propagate(False)  # Fix the size
            
            # Image placeholder
            img_frame = tk.Frame(card, bg="white", height=180)
            img_frame.pack(fill=tk.X)
            img_frame.pack_propagate(False)
            
            tk.Label(img_frame, text="CAR IMAGE", bg="white", font=("Arial", 14, "bold")).place(relx=0.5, rely=0.5, anchor="center")
            
            # Car info
            info_text = f"{item['Make']} {item['Model']}"
            if 'Color' in item and item['Color']:
                info_text += f" - {item['Color']}"
                
            info_label = tk.Label(card, text=info_text, bg="white")
            info_label.pack(pady=5)
            
            # Make the entire card clickable
            img_frame.bind("<Button-1>", lambda e, i=item: self.display_item_details(i))
            info_label.bind("<Button-1>", lambda e, i=item: self.display_item_details(i))

    def display_results(self, results):
        # Display search results as a grid of car cards
        #self.clear_window()
        #self.main_menu()  # Recreate the main layout
        self.results_frame.destroy()
        self.results_frame = tk.Frame(self.content_frame, bg="white")
        self.results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.display_catalog_grid(results)  # Display results in the grid

    def display_item_details(self, item):
        # Displays detailed information about a selected item
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        self.clear_window()
        frame = tk.Frame(self.root, bg="white")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add back button at the top
        back_button = tk.Button(frame, text="← Back", command=lambda: self.display_results(self.DB.get_car_catalog()), 
                               bg="#4682B4", fg="white")
        back_button.pack(anchor="nw", pady=10)

        details_frame = tk.Frame(frame, bg="white", padx=20, pady=20)
        details_frame.pack(fill=tk.BOTH, expand=True)

        for key, value in item.items():
            if key == 'Video' and value:
                #tk.Label(details_frame, text=f"{key}:", font=("Arial", 12, "bold"), bg="white").pack()
                ##player = TkinterVideo(details_frame, scaled=True, bg="white")
                ##player.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                ##player._keep_aspect_ratio = True
                ##player.load(value)
                ##player.bind("<Map>", lambda e: player.place(relwidth=0.5, relheight=0.5, relx=0.5, rely=0.7, anchor="center"))
                ##player.play()
                continue
            elif value:
                tk.Label(details_frame, text=f"{key}: {value}", font=("Arial", 12), bg="white").pack(anchor="w")
        
        button_frame = tk.Frame(details_frame, bg="white")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Update", command=lambda: self.update_item(item.get('ID')), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove", command=lambda: self.remove_item(item.get('ID')), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)

    def view_item(self):
        item_id = simpledialog.askstring("View Item", "Enter item ID:")
        item = self.DB.get_car(item_id)
        self.text = ""
        self.display_item_details(item)

    def add_item(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Add Item", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        labels = [label + ":" for label in self.DB.get_categories()[1:]]
        entries = [tk.Entry(frame) for _ in self.DB.get_categories()[1:]]

        for label, entry in zip(labels, entries):
            tk.Label(frame, text=label, bg="white").pack()
            entry.pack()

        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(pady=10)
        tk.Button(
            button_frame,
            text="Add",
            command=lambda: self.send_info(entries),
            bg="#4682B4", fg="white"
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=lambda: self.display_results(self.DB.get_car_catalog()), 
                 bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)
    
    def update_item(self, ID=None):
        if ID is None:
            ID = simpledialog.askstring("Update Item", "Enter item ID to update:")
        item = self.DB.get_car(ID)
        if not item:
            messagebox.showerror("Error", "Item not found")
            return
        
        self.clear_window()
        frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Update Item", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        labels = [label + ":" for label in self.DB.get_categories()[1:]]
        entries = [tk.Entry(frame) for _ in self.DB.get_categories()[1:]]

        for label, entry in zip(labels, entries):
            tk.Label(frame, text=label, bg="white").pack()
            entry.insert(0, item.get(label.strip(": ")))
            entry.pack()

        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(pady=10)
        tk.Button(
            button_frame,
            text="Update",
            command=lambda: self.send_info(entries, ID),
            bg="#4682B4", fg="white"
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=lambda: self.display_results(self.DB.get_car_catalog()), 
                 bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)

    def send_info(self, entries, ID=None):
        if ID:
            car_info = dict({"ID": ID}, **{key: entry.get() for key, entry in zip(self.DB.get_categories()[1:], entries)})
        else:
            # If no previous ID is provided, generate a new one based on the last element in the catalog
            car_info = dict({"ID": str(int(self.DB.get_car_catalog()[-1].get("ID"))+1)}, **{key: entry.get() for key, entry in zip(self.DB.get_categories()[1:], entries)})
        if car_info["Model"] and car_info["Year"].isdigit():
            if ID:
                self.DB.update_car(car_info)
            else:
                self.DB.add_car(car_info)
            self.display_results(self.DB.get_car_catalog()) 
        else:
            # Maybe better error message for what is wrong specifics?
            messagebox.showerror("Error", "Either missing Model or incorrect Year")

    def remove_item(self, ID=None):
        if not ID:
            ID = simpledialog.askstring("Remove Item", "Enter item ID to remove:")
        if ID:
            if (not self.DB.if_exist(ID)):
                messagebox.showinfo("Error", "Car does not exist")
            else:
                confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove this item?")
                if confirm:
                    self.DB.remove_car(ID)
                    messagebox.showinfo("Success", "Car removed successfully")
        self.display_results(self.DB.get_car_catalog())

    def on_closing(self):
        if messagebox.askyesno("Save Catalog", "Would you like to save the catalog before exiting?"):
            self.on_save()
        self.root.destroy()
    
    def on_save(self):
        self.DB.save_catalog()
        messagebox.showinfo("Success", "Catalog saved successfully")

    def clear_window(self):
        # Clears all widgets from the window before updating the UI
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    CatalogApp(root)
    root.mainloop()
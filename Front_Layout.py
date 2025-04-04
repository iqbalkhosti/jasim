import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
#from tkVideoPlayer import TkinterVideo
from database_backend import Database

#pip install Pillow 
class CatalogApp:
    text = ""
    DB = Database()
    def __init__(self, root):
        # Initialize the application window with a title, size, and background color
        # Calls the login screen method to start the application
        self.root = root
        self.root.title("Catalog System")
        self.root.geometry("900x600")  # Increased size to match mockup
        self.root.configure(bg="white")
        self.login_screen()
        self.current_view = 'main'

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
            if(key != "ID" and key != "Video" and key != "ImageURL"):
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
        # Create popup menu
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Display Catalog", command=lambda: self.display_results(self.DB.get_car_catalog()))
        menu.add_command(label="View Item Details", command=self.view_item)
        menu.add_command(label="Add Entry", command=self.add_item)
        menu.add_command(label="Update Entry", command=self.update_item)
        menu.add_command(label="Remove Entry", command=self.remove_item)
        menu.add_command(label="Save Catalog", command=self.on_save)
        menu.add_command(label="Favorites", command=self.show_favorites)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.on_closing)

        # Calculate menu position
        menu.update_idletasks()  # Force geometry calculation
        menu_width = menu.winfo_width()
        menu_height = menu.winfo_height()
        
        # Get button position
        button_x = self.menu_button.winfo_rootx()
        button_y = self.menu_button.winfo_rooty()
        button_height = self.menu_button.winfo_height()
        
        # Get window dimensions
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Calculate positions
        x = button_x - menu_width  # Open to the left of the button
        y = button_y + button_height
        
        # Adjust if near screen edges
        if x < self.root.winfo_rootx():
            x = button_x  # Open to the right if not enough space on left
        if y + menu_height > self.root.winfo_rooty() + window_height:
            y = self.root.winfo_rooty() + window_height - menu_height
        
        menu.tk_popup(x, y)

    def search(self, from_menu=False):
        if from_menu:
            self.text = self.search_entry.get()
            if self.text == "Search":
                self.text = ""
        print(self.terms)
        self.display_results(self.DB.search(self.text))

    def display_catalog_grid(self, results):
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
        if not results:
            tk.Label(self.results_frame, text="No results found", bg="white").pack()
            return
        
        # Create a canvas with a scrollbar
        canvas = tk.Canvas(self.results_frame, bg="white")
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create grid layout within the scrollable frame
        row_frame = None
        for idx, item in enumerate(results):
            # Create a new row for every 3 items
            if idx % 3 == 0:
                row_frame = tk.Frame(scrollable_frame, bg="white")
                row_frame.pack(fill=tk.X, pady=5)
            
            # Create card for each item
            card = tk.Frame(row_frame, bd=1, relief=tk.SOLID, bg="white", width=200, height=250)
            card.pack(side=tk.LEFT, padx=5, fill=tk.BOTH)
            card.pack_propagate(False)  # Fix the size
            
            # Image container with fixed size
            img_frame = tk.Frame(card, bg="white", height=180)
            img_frame.pack(fill=tk.X)
            img_frame.pack_propagate(False)
            
            # Load image or show placeholder
            image_url = item.get("ImageURL", "")
            if image_url:
                try:
                    with urllib.request.urlopen(image_url) as url_response:
                        image_data = url_response.read()
                    image = Image.open(BytesIO(image_data))
                    image = image.resize((200, 180), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    img_label = tk.Label(img_frame, image=photo, bg="white")
                    img_label.image = photo  # Keep reference
                    img_label.pack(fill=tk.BOTH, expand=True)
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.create_placeholder(img_frame, "Failed to load image")
            else:
                self.create_placeholder(img_frame, "No image available")
            
            # Car info (always shown regardless of image)
            info_text = f"{item['Make']} {item['Model']}"
            if 'Color' in item and item['Color']:
                info_text += f" - {item['Color']}"
            
            info_frame = tk.Frame(card, bg="white")
            info_frame.pack(fill=tk.X, pady=5)
            
            info_label = tk.Label(info_frame, text=info_text, bg="white", wraplength=180)
            info_label.pack()
            
            # Make the entire card clickable
            img_frame.bind("<Button-1>", lambda e, i=item: self.display_item_details(i))
            info_label.bind("<Button-1>", lambda e, i=item: self.display_item_details(i))

            if self.current_view == 'favorites':
                button_frame = tk.Frame(card, bg="white")
                button_frame.pack(pady=5)
                remove_btn = tk.Button(button_frame, text="Remove from Favorites",
                                      command=lambda cid=item['ID']: self.remove_from_favorites(cid))
                remove_btn.pack()
    
    def remove_from_favorites(self, car_id):
        self.DB.remove_favorite(car_id)
        self.show_favorites()

    def create_placeholder(self, parent, text):
        placeholder = tk.Frame(parent, bg="lightgray", height=180)
        placeholder.pack(fill=tk.BOTH, expand=True)
        tk.Label(placeholder, text=text, bg="lightgray", fg="black", 
                font=("Arial", 10)).place(relx=0.5, rely=0.5, anchor="center")
        return placeholder

    # Updated display_item_details to handle images better
    def display_item_details(self, item):
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        self.clear_window()
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Back button
        back_button = tk.Button(main_frame, text="← Back", 
                            command=lambda: self.display_results(self.DB.get_car_catalog()), 
                            bg="#4682B4", fg="white")
        back_button.grid(row=0, column=0, columnspan=2, sticky="nw", pady=10)

        # Configure grid layout
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)  # Prevent vertical stretching

        # Square Image Panel (400x400)
        image_panel = tk.Frame(main_frame, bg="lightgray", width=400, height=400)
        image_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        image_panel.pack_propagate(False)  # Maintain fixed size

        # Load image or show placeholder
        image_url = item.get("ImageURL", "")
        if image_url:
            try:
                with urllib.request.urlopen(image_url) as url_response:
                    image_data = url_response.read()
                image = Image.open(BytesIO(image_data))
                image = image.resize((400, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                img_label = tk.Label(image_panel, image=photo, bg="lightgray")
                img_label.image = photo
                img_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                tk.Label(image_panel, text="Image Load Error\n" + str(e), 
                        bg="lightgray", wraplength=380).pack(pady=20)
        else:
            tk.Label(image_panel, text="No Image Available", 
                    bg="lightgray", font=("Arial", 14)).pack(pady=20)

        # Rectangular Details Panel (400x400)
        details_panel = tk.Frame(main_frame, bg="white", width=400, height=400)
        details_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        details_panel.grid_propagate(False)  # Maintain fixed size

        # Scrollable details area
        canvas = tk.Canvas(details_panel, bg="white")
        scrollbar = ttk.Scrollbar(details_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Details content
        row = 0
        for key, value in item.items():
            if key in ['Video', 'ImageURL'] or not value:
                continue
            tk.Label(scrollable_frame, text=f"{key}:", 
                    font=("Arial", 12, "bold"), 
                    bg="white", anchor="w").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            tk.Label(scrollable_frame, text=value, 
                    font=("Arial", 12), 
                    bg="white", anchor="w", wraplength=350).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            row += 1

        # Centered buttons at bottom of details panel
        button_frame = tk.Frame(details_panel, bg="white")
        button_frame.place(relx=0.5, rely=0.95, anchor="center")  # 95% down the panel
        
        tk.Button(button_frame, text="Update", 
                command=lambda: self.update_item(item.get('ID')), 
                bg="#4682B4", fg="white", width=12).pack(side="left", padx=10)
        tk.Button(button_frame, text="Remove", 
                command=lambda: self.remove_item(item.get('ID')), 
                bg="#4682B4", fg="white", width=12).pack(side="left", padx=10)
        
        fav_text = "Add to Favorites" if not self.DB.is_favorite(item.get('ID')) else "Remove from Favorites"
        tk.Button(button_frame, text=fav_text, command=lambda: self.toggle_favorite(item.get('ID')),
                  bg="#4682B4", fg="white", width=16).pack(side=tk.LEFT, padx=10)
            
    def toggle_favorite(self, car_id):
        if self.DB.is_favorite(car_id):
            self.DB.remove_favorite(car_id)
        else:
            self.DB.add_favorite(car_id)
        # Refresh details view
        item = self.DB.get_car(car_id)
        self.display_item_details(item)

    def show_favorites(self):
        self.display_results(self.DB.get_favorites(), view='favorites')

    def display_results(self, results, view='main'):
        # Display search results as a grid of car cards
        #self.clear_window()
        #self.main_menu()  # Recreate the main layout
        try:
            self.results_frame.destroy()
            self.results_frame = tk.Frame(self.content_frame, bg="white")
            self.results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        except:
            self.clear_window()
            self.main_menu()
            self.results_frame.destroy()
            self.results_frame = tk.Frame(self.content_frame, bg="white")
            self.results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.display_catalog_grid(results)  # Display results in the grid

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
        print(car_info)
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

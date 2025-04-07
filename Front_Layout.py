import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import urllib.request
from io import BytesIO
from tkVideoPlayer import TkinterVideo
from LoginUI import LoginUI
from database_backend import Database
import os

# The CatalogApp class defines the main application for a car catalog system.
class CatalogApp:
    text = ""  # Stores search text input by the user.
    filter_map = {}  # Holds all possible filters by category.
    terms = []  # A list to store search terms derived from the filter selections.
    DB = Database()  # An instance of the database backend to interact with car data.

    def __init__(self, root):
        # Constructor that initializes the main window settings
        self.root = root
        self.root.title("Catalog System")
        self.root.geometry("900x600")  # Sets a window size of 900x600 pixels.
        self.root.configure(bg="white")  # Uses a white background for the window.
        self.current_view = 'main'
        self.DB = Database()  # Initializes a fresh instance of the database.
        self._initialize_ui()  # Calls the method to initialize the user interface.

    def _initialize_ui(self):
        # Start the UI by launching the login screen.
        self.login_ui = LoginUI(self.root, self._handle_login_success)

    def _handle_login_success(self, user_type, username):
        # Callback after a successful login.
        self.user_type = user_type  # Sets the user type (admin or regular).
        self.current_user = username  # Sets the current user's username.
        self._setup_admin_features()  # If the user is an admin, enable extra features.
        self.main_menu()  # Launch the main menu once logged in.

    def _setup_admin_features(self):
        # If the user is an admin, enable administrator-specific features.
        if self.user_type == 'admin':
            print("Admin features enabled")  # Placeholder for future admin-specific code.

    def generate_filter_map(self):
        # Generates a mapping of filter categories to a list of unique filter values.
        # Excludes certain categories (ID, Video, ImageURL) that should not be used for filtering.
        for key in self.DB.get_categories():
            if key != "ID" and key != "Video" and key != "ImageURL":
                # Creates a sorted list of unique values for the category.
                filter_list = list({d[key] for d in self.DB.get_car_catalog()})
                filter_list = sorted(filter_list)
                self.filter_map[key] = filter_list

    def main_menu(self, first_gen=True):
        # Displays the main menu which includes the search bar, filter dropdowns, and catalog results.
        self.clear_window()  # Clears the window of any existing widgets.

        # Create a main frame to contain the UI elements.
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a top bar for the search bar and menu button.
        top_frame = tk.Frame(main_frame, bg="white", bd=1, relief=tk.SOLID)
        top_frame.pack(fill=tk.X, padx=0, pady=0)

        # Left side of the top bar for the search input.
        search_frame = tk.Frame(top_frame, bg="white")
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)

        # Create the search entry widget.
        self.search_entry = tk.Entry(search_frame, width=80, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Search")  # Default text in the search bar.
        # Bind events to clear the placeholder text on focus.
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "Search" else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "Search") if not self.search_entry.get() else None)
        self.search_entry.bind("<Return>", lambda e: self.search(True))  # Execute search on pressing Enter.

        # Right side of the top bar for the menu button.
        menu_frame = tk.Frame(top_frame, bg="white")
        menu_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        # The menu button displays a hamburger icon.
        self.menu_button = tk.Button(menu_frame, text="≡", font=("Arial", 16), bg="white", bd=1, command=self.show_menu_dropdown)
        self.menu_button.pack(side=tk.RIGHT)

        # Content area is split into a left panel (filters) and a right panel (results).
        self.content_frame = tk.Frame(main_frame, bg="white")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Create a canvas to allow scrolling for the filter panel.
        canvas = tk.Canvas(self.content_frame, bg="white", width=240)  # Fixed width for filter panel.
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        # Update the canvas scroll region whenever the scrollable frame's size changes.
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill=tk.Y, expand=False)
        scrollbar.pack(side="left", fill="y")

        # Filter panel inside the scrollable frame.
        filter_frame = tk.Frame(scrollable_frame, bg="white", width=240)
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Generate the filter mapping from the database.
        self.generate_filter_map()

        # Create a dropdown for each filter category (excluding ID, Video, and ImageURL).
        for key in self.DB.get_categories():
            if key != "ID" and key != "Video" and key != "ImageURL":
                self.create_filter_dropdown(filter_frame, key)

        # Right side: Create a frame to hold the catalog result grid.
        if first_gen:
            self.results_frame = tk.Frame(self.content_frame, bg="white")
            self.results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            # Display the initial catalog grid with all car items.
            self.display_catalog_grid(self.DB.get_car_catalog())

    def create_filter_dropdown(self, parent, title):
        # Creates an expandable dropdown menu for a given filter category.
        frame = tk.Frame(parent, bg="white", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.X, padx=5, pady=5)

        # Header for the dropdown containing the title and toggle button.
        header_frame = tk.Frame(frame, bg="white")
        header_frame.pack(fill=tk.X)

        # Variable to track whether the dropdown is expanded or collapsed.
        is_expanded = tk.BooleanVar(value=False)

        # Function to toggle the dropdown state.
        def toggle_dropdown():
            is_expanded.set(not is_expanded.get())
            if is_expanded.get():
                content_frame.pack(fill=tk.X, pady=5)
                toggle_button.config(text="v")
            else:
                content_frame.pack_forget()
                toggle_button.config(text=">")

        # Label for the category title.
        tk.Label(header_frame, text=title, font=("Arial", 12, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
        # Toggle button for expand/collapse.
        toggle_button = tk.Button(header_frame, text=">", bg="white", bd=0, command=toggle_dropdown)
        toggle_button.pack(side=tk.RIGHT, padx=5)

        # Frame that holds the checkbox filters.
        content_frame = tk.Frame(frame, bg="white", padx=10)
        # Add checkboxes for each filter value in the category.
        filter_vars = []
        filter_list = self.filter_map.get(title)
        for filter in filter_list:
            var = tk.BooleanVar()
            filter_vars.append(var)
            cb = tk.Checkbutton(content_frame, text=filter, variable=var, bg="white", command=self.apply_filters)
            cb.pack(anchor="w")

        # Save the checkbox variables so they can be accessed later (e.g., when applying filters).
        if not hasattr(self, 'filter_checkboxes'):
            self.filter_checkboxes = {}
        self.filter_checkboxes[title] = filter_vars

    def apply_filters(self):
        # Called when any filter checkbox is toggled.
        # Clears previous filter terms and rebuilds the search term list based on the selected filters.
        self.terms.clear()
        if hasattr(self, 'filter_checkboxes'):
            for title, checkbox_vars in self.filter_checkboxes.items():
                filter_list = self.filter_map[title]
                for i, var in enumerate(checkbox_vars):
                    if var.get():
                        if filter_list[i] not in self.text:
                            self.terms.append(filter_list[i])
        self.search()  # Perform a search using the new filter terms.

    def show_menu_dropdown(self):
        # Creates and displays a popup menu when the menu button is clicked.
        menu = tk.Menu(self.root, tearoff=0)
        # Add menu commands for various actions such as displaying the catalog, viewing details, and admin options.
        menu.add_command(label="Display Catalog", command=lambda: self.display_results(self.DB.get_car_catalog()))
        menu.add_command(label="View Item Details", command=self.view_item)
        if self.user_type == 'admin':
            menu.add_command(label="Add Entry", command=self.add_item)
            menu.add_command(label="Update Entry", command=self.update_item)
            menu.add_command(label="Remove Entry", command=self.remove_item)
            menu.add_command(label="Save Catalog", command=self.on_save)
        menu.add_command(label="Favorites", command=self.show_favorites)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.on_closing)

        # Calculate the menu's position relative to the menu button.
        menu.update_idletasks()  # Ensure geometry is calculated.
        menu_width = menu.winfo_width()
        menu_height = menu.winfo_height()
        button_x = self.menu_button.winfo_rootx()
        button_y = self.menu_button.winfo_rooty()
        button_height = self.menu_button.winfo_height()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = button_x - menu_width  # Default to showing menu on the left.
        y = button_y + button_height
        # Adjust position if near the screen edges.
        if x < self.root.winfo_rootx():
            x = button_x
        if y + menu_height > self.root.winfo_rooty() + window_height:
            y = self.root.winfo_rooty() + window_height - menu_height

        menu.tk_popup(x, y)

    def search(self, from_menu=False):
        # Retrieves the search text from the search entry and combines it with selected filter terms.
        if from_menu:
            self.text = self.search_entry.get()
            if self.text == "Search":
                self.text = ""
        temp = (self.text.lower().split())
        # Calls the database search method with both filter terms and free text search terms.
        self.display_results(self.DB.search(self.terms + temp))

    def display_catalog_grid(self, results):
        # Displays the catalog items in a grid layout.
        # First, clear any existing widgets from the results frame.
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if not results:
            tk.Label(self.results_frame, text="No results found", bg="white").pack()
            return

        # Create a canvas with a scrollbar for displaying a large number of results.
        canvas = tk.Canvas(self.results_frame, bg="white")
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create a grid of cards, where each card represents an item from the catalog.
        row_frame = None
        for idx, item in enumerate(results):
            # For every three items, create a new row.
            if idx % 3 == 0:
                row_frame = tk.Frame(scrollable_frame, bg="white")
                row_frame.pack(fill=tk.X, pady=5)
            # Create a card with fixed dimensions.
            card = tk.Frame(row_frame, bd=1, relief=tk.SOLID, bg="white", width=200, height=250)
            card.pack(side=tk.LEFT, padx=5, fill=tk.BOTH)
            card.pack_propagate(False)  # Prevent the card from resizing.

            # Container for the image with a fixed height.
            img_frame = tk.Frame(card, bg="white", height=180)
            img_frame.pack(fill=tk.X)
            img_frame.pack_propagate(False)

            # Attempt to load the image from a URL; if unavailable, show a placeholder.
            image_url = item.get("ImageURL", "")
            if image_url:
                try:
                    with urllib.request.urlopen(image_url, timeout=1) as url_response:
                        image_data = url_response.read()
                    image = Image.open(BytesIO(image_data))
                    image = image.resize((200, 180), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    img_label = tk.Label(img_frame, image=photo, bg="white")
                    img_label.image = photo  # Keep a reference to avoid garbage collection.
                    img_label.pack(fill=tk.BOTH, expand=True)
                except Exception as e:
                    print(f"Error loading image: {e}")
                    self.create_placeholder(img_frame, "Failed to load image")
            else:
                self.create_placeholder(img_frame, "No image available")

            # Display basic car info (Make, Model, and Color if available).
            info_text = f"{item['Make']} {item['Model']}"
            if 'Color' in item and item['Color']:
                info_text += f" - {item['Color']}"
            info_frame = tk.Frame(card, bg="white")
            info_frame.pack(fill=tk.X, pady=5)
            info_label = tk.Label(info_frame, text=info_text, bg="white", wraplength=180)
            info_label.pack()

            # Bind click events so that clicking the image or info opens detailed view.
            img_frame.bind("<Button-1>", lambda e, i=item: self.display_item_details(i))
            info_label.bind("<Button-1>", lambda e, i=item: self.display_item_details(i))

            # If the current view is 'favorites', add a remove button.
            if self.current_view == 'favorites':
                button_frame = tk.Frame(card, bg="white")
                button_frame.pack(pady=5)
                remove_btn = tk.Button(button_frame, text="Remove from Favorites",
                                       command=lambda cid=item['ID']: self.remove_from_favorites(cid))
                remove_btn.pack()

    def remove_from_favorites(self, car_id):
        # Removes an item from the favorites list in the database and refreshes the favorites view.
        self.DB.remove_favorite(car_id)
        self.show_favorites()

    def create_placeholder(self, parent, text):
        # Creates a placeholder frame with a message when an image fails to load.
        placeholder = tk.Frame(parent, bg="lightgray", height=180)
        placeholder.pack(fill=tk.BOTH, expand=True)
        tk.Label(placeholder, text=text, bg="lightgray", fg="black", font=("Arial", 10)).place(relx=0.5, rely=0.5, anchor="center")
        return placeholder

    def display_item_details(self, item):
        # Displays a detailed view of a single catalog item.
        if not item:
            messagebox.showerror("Error", "Item not found")
            return

        self.clear_window()  # Clear the main window.
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Back button to return to the previous view.
        back_button = tk.Button(main_frame, text="← Back", 
                                command=lambda: self.display_results(self.DB.search(self.terms)) if self.terms else self.display_results(self.DB.get_car_catalog()), 
                                bg="#4682B4", fg="white")
        back_button.grid(row=0, column=0, columnspan=2, sticky="nw", pady=10)

        # Set up the grid layout for image and details.
        main_frame.grid_columnconfigure(0, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)  # Prevent vertical stretching.

        # Panel for displaying a large square image.
        image_panel = tk.Frame(main_frame, bg="lightgray", width=400, height=400)
        image_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        image_panel.pack_propagate(False)

        # Load and display the image from URL or show a placeholder if unavailable.
        image_url = item.get("ImageURL", "")
        if image_url:
            try:
                with urllib.request.urlopen(image_url, timeout=1) as url_response:
                    image_data = url_response.read()
                image = Image.open(BytesIO(image_data))
                image = image.resize((400, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                img_label = tk.Label(image_panel, image=photo, bg="lightgray")
                img_label.image = photo
                img_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                tk.Label(image_panel, text="Image Load Error\n" + str(e), bg="lightgray", wraplength=380).pack(pady=20)
                img_label = None
        else:
            tk.Label(image_panel, text="No Image Available", bg="lightgray", font=("Arial", 14)).pack(pady=20)
            img_label = None

        # If a video path is provided and an image is loaded, enable video playback.
        videoPath = item.get("Video", "")
        if videoPath and img_label:
            def toggle_video(event=None):
                nonlocal is_video_playing
                if not is_video_playing:
                    img_label.pack_forget()  # Hide image to show video.
                    player.seek(0)
                    player.play()
                    is_video_playing = True
                else:
                    player.pause()
                    img_label.pack(fill=tk.BOTH, expand=True)
                    is_video_playing = False

            if os.path.exists(videoPath):
                video_frame = tk.Frame(image_panel, bg="white")
                video_frame.pack(fill=tk.BOTH, expand=True)
                player = TkinterVideo(video_frame, scaled=True, bg="white")
                player.pack(fill=tk.BOTH, expand=True)
                player._keep_aspect_ratio = True
                player.load(videoPath)
                # Bind click events to toggle between video and image view.
                img_label.bind("<Button-1>", toggle_video)
                player.bind("<Button-1>", toggle_video)

            is_video_playing = False  # Initial state: video is not playing.

        # Panel for showing the item details in a scrollable area.
        details_panel = tk.Frame(main_frame, bg="white", width=400, height=400)
        details_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        details_panel.grid_propagate(False)

        # Create a canvas with a vertical scrollbar for the details.
        canvas = tk.Canvas(details_panel, bg="white")
        scrollbar = ttk.Scrollbar(details_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display each detail (key-value pair) except for Video and ImageURL.
        row = 0
        for key, value in item.items():
            if key in ['Video', 'ImageURL'] or not value:
                continue
            tk.Label(scrollable_frame, text=f"{key}:", font=("Arial", 12, "bold"), bg="white", anchor="w").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            tk.Label(scrollable_frame, text=value, font=("Arial", 12), bg="white", anchor="w", wraplength=350).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            row += 1

        # Button frame at the bottom for actions like updating, removing, or favoriting the item.
        button_frame = tk.Frame(details_panel, bg="white")
        button_frame.place(relx=0.5, rely=0.95, anchor="center")
        if self.user_type == 'admin':
            tk.Button(button_frame, text="Update", command=lambda: self.update_item(item.get('ID')), bg="#4682B4", fg="white", width=12).pack(side="left", padx=10)
            tk.Button(button_frame, text="Remove", command=lambda: self.remove_item(item.get('ID')), bg="#4682B4", fg="white", width=12).pack(side="left", padx=10)
        fav_text = "Add to Favorites" if not self.DB.is_favorite(item.get('ID')) else "Remove from Favorites"
        tk.Button(button_frame, text=fav_text, command=lambda: self.toggle_favorite(item.get('ID')), bg="#4682B4", fg="white", width=16).pack(side=tk.LEFT, padx=10)

    def toggle_favorite(self, car_id):
        # Toggles whether an item is marked as favorite in the database.
        if self.DB.is_favorite(car_id):
            self.DB.remove_favorite(car_id)
        else:
            self.DB.add_favorite(car_id)
        # Refresh the details view to update the favorite status.
        item = self.DB.get_car(car_id)
        self.display_item_details(item)

    def show_favorites(self):
        # Displays all items marked as favorites.
        self.display_results(self.DB.get_favorites(), view='favorites')

    def display_results(self, results, view='main'):
        # Displays a set of search results or catalog items in the results frame.
        try:
            self.results_frame.destroy()
            self.results_frame = tk.Frame(self.content_frame, bg="white")
            self.results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        except:
            self.clear_window()
            self.main_menu(False)
            self.results_frame.destroy()
            self.results_frame = tk.Frame(self.content_frame, bg="white")
            self.results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.display_catalog_grid(results)

    def view_item(self):
        # Prompts the user for an item ID and displays details for that item.
        item_id = simpledialog.askstring("View Item", "Enter item ID:")
        item = self.DB.get_car(item_id)
        self.text = ""
        self.display_item_details(item)

    def add_item(self):
        # Allows administrators to add a new item to the catalog.
        if self.user_type != 'admin':
            messagebox.showerror("Permission Denied", "Only administrators can add entries.")
            return
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
        tk.Button(button_frame, text="Add", command=lambda: self.send_info(entries), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=lambda: self.display_results(self.DB.get_car_catalog()), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)

    def update_item(self, ID=None):
        # Allows administrators to update an existing catalog entry.
        if self.user_type != 'admin':
            messagebox.showerror("Permission Denied", "Only administrators can update entries.")
            return
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
            entry.insert(0, item.get(label.strip(": ")))  # Pre-fill entry with existing item value.
            entry.pack()
        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Update", command=lambda: self.send_info(entries, ID), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=lambda: self.display_results(self.DB.get_car_catalog()), bg="#4682B4", fg="white").pack(side=tk.LEFT, padx=5)

    def send_info(self, entries, ID=None):
        # Collects data from entry fields and either adds a new catalog item or updates an existing one.
        if ID:
            car_info = dict({"ID": ID}, **{key: entry.get() for key, entry in zip(self.DB.get_categories()[1:], entries)})
        else:
            # If adding a new item, auto-generate a new ID based on the last item in the catalog.
            car_info = dict({"ID": str(int(self.DB.get_car_catalog()[-1].get("ID")) + 1)},
                            **{key: entry.get() for key, entry in zip(self.DB.get_categories()[1:], entries)})
        # Simple validation: checks that 'Model' is provided and 'Year' is numeric.
        if car_info["Model"] and car_info["Year"].isdigit():
            if ID:
                self.DB.update_car(car_info)
            else:
                self.DB.add_car(car_info)
            self.display_results(self.DB.get_car_catalog())
        else:
            messagebox.showerror("Error", "Either missing Model or incorrect Year")

    def remove_item(self, ID=None):
        # Allows administrators to remove an item from the catalog.
        if self.user_type != 'admin':
            messagebox.showerror("Permission Denied", "Only administrators can remove entries.")
            return
        if not ID:
            ID = simpledialog.askstring("Remove Item", "Enter item ID to remove:")
        if ID:
            if not self.DB.if_exist(ID):
                messagebox.showinfo("Error", "Car does not exist")
            else:
                confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove this item?")
                if confirm:
                    self.DB.remove_car(ID)
                    messagebox.showinfo("Success", "Car removed successfully")
        self.display_results(self.DB.get_car_catalog())

    def on_closing(self):
        # Handles the closing of the application.
        if self.user_type == 'admin':
            if messagebox.askyesno("Save Catalog", "Would you like to save the catalog before exiting?"):
                self.on_save()
        self.root.destroy()

    def on_save(self):
        # Saves the current state of the catalog if the user is an administrator.
        if self.user_type != 'admin':
            messagebox.showerror("Permission Denied", "Only administrators can save the catalog.")
            return
        self.DB.save_catalog()
        messagebox.showinfo("Success", "Catalog saved successfully")

    def clear_window(self):
        # Removes all widgets from the main window to prepare for a new screen.
        for widget in self.root.winfo_children():
            widget.destroy()

# Main entry point: create a Tkinter window and run the CatalogApp.
if __name__ == "__main__":
    root = tk.Tk()
    CatalogApp(root)
    root.mainloop()

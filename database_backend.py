import csv

class Database:
    # Class-level lists to store car data, categories, and favorite cars.
    car_catalog = []  # list for storing all information about cars (not used in methods directly)
    categories = []   # list for storing all possible categories (not used directly, but updated in __init__)
    fav_cars = []     # list for storing favorite cars of users

    # Constructor: reads the car catalog from "database.csv" when an instance is created.
    def __init__(self):
        # Open the CSV file in read mode.
        with open("database.csv", "r") as file:
            reader = csv.DictReader(file)
            # Load each row (car record) as a dictionary into self.catalog.
            self.catalog = [row for row in reader]
            # Save the CSV header (column names) as categories.
            self.categories = reader.fieldnames

        # The following block is commented out.
        # It was used to ensure that an "ImageURL" field exists in the CSV.
        # If missing, it adds the "ImageURL" category and sets a default empty value for each car.
        # if "ImageURL" not in self.categories:
        #     self.categories.append("ImageURL")
        #     for car in self.catalog:
        #         car["ImageURL"] = car.get("ImageURL", "")  # Initialize empty if missing

    # Method to add a new car to the catalog.
    def add_car(self, car_info):
        # Check if the "Year" is a valid number.
        if not car_info["Year"].isdigit():
            print("Invalid Year. Year must be a number.")
            return
        # Inform the user that for bulk adding, they should modify the CSV directly.
        print("For bulk adding, please edit CSV directly")
        # Append the new car info (dictionary) to the catalog list.
        self.catalog.append(car_info)

    # Method to update an existing car in the catalog.
    def update_car(self, car_info):
        # Loop through each car record in the catalog.
        for item in self.catalog:
            # When a match on the "ID" is found, update that car's information.
            if item["ID"] == car_info["ID"]:
                item.update(car_info)
                break

    # Method to remove a car from the catalog.
    def remove_car(self, ID):
        # Iterate over the catalog to find the car with the specified ID.
        for item in self.catalog:
            if item["ID"] == ID:
                self.catalog.remove(item)  # Remove the found car from the catalog.
                break
        # Also remove the car from the favorites list to keep data consistent.
        self.remove_favorite(ID)

    # Checks whether a car with a specific ID exists in the catalog.
    def if_exist(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                return True
        return False

    # Method to save the current catalog data back into "database.csv".
    def save_catalog(self):
        # Open the CSV file in write mode.
        with open("database.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.categories)
            writer.writeheader()      # Write the header (categories).
            writer.writerows(self.catalog)  # Write all car records.

    '''
    Search method to find specific car records based on a list of search terms.
    If exact matches are not found, it uses a relevance threshold.
    '''
    def search(self, terms, relevance=False):
        # Remove duplicate terms from the search list.
        terms = list(dict.fromkeys(terms))
        print(terms)
        results = []  # List to store matching results.

        '''
        The commented-out code below was the original search implementation.
        It was removed for being hard to understand and manipulate.
        '''
        #results = [item for item in self.get_car_catalog() if all(any(term in str(item[category]).lower() for category in self.get_categories()) for term in terms)] if terms else self.get_car_catalog()

        # Loop through each car record.
        for item in self.get_car_catalog():
            # Create a set of lowercase search terms.
            terms_set = {term.lower() for term in terms}
            # Create a set of all lowercase values for the current car record.
            values_set = {value.lower() for value in item.values()}

            if relevance == True:
                # Calculate the threshold: proportion of search terms that match the car's values.
                threshold = (len(terms_set & values_set)) / len(terms)
                # Include this car if at least 40% of the terms match.
                if threshold >= 0.4:
                    results.append(item)
            else:
                # For perfect matches, check if every search term is found in the car's values.
                if terms_set.issubset(values_set):
                    results.append(item)

        '''
        If no results are found without using relevance checking, then try again with relevance mode.
        '''
        if len(results) == 0 and relevance is False:
            results = self.search(terms, True)
        return results

    # Getter method to return the entire car catalog.
    def get_car_catalog(self):
        return self.catalog

    # Getter method to return the list of categories (column names).
    def get_categories(self):
        return self.categories

    # Getter method to return a single car record based on its ID.
    def get_car(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                return item
        return None

    # Original method for saving a favorite car based on several properties.
    def save_fav_car(self, make, model, year, color):
        # Loop through each car in the catalog.
        for i in self.catalog:
            # If the car matches all provided attributes, add it to the favorites list.
            if(i.get("Make") == make and i.get("Model") == model and i.get("Year") == str(year) and i.get("Color") == color):
                self.fav_cars.append(i)

    # Method to filter favorite cars based on an input value.
    def filter_fav_cars(self, input2):
        self.filtered_list = []
        # Loop through each favorite car.
        for d in self.fav_cars:
            # Check each value in the car record.
            for value in d.values():
                if input2 in value:
                    self.filtered_list.append(d)
        return self.filtered_list

    # Improved method for adding a car to favorites using the car ID.
    def add_favorite(self, car_id):
        # Retrieve the car by ID.
        car = self.get_car(car_id)
        # Add the car to favorites if it exists and is not already a favorite.
        if car and not self.is_favorite(car_id):
            self.fav_cars.append(car)

    # Method for removing a car from the favorites list based on its ID.
    def remove_favorite(self, car_id):
        # Use list comprehension to remove any car with the matching ID.
        self.fav_cars = [fav_car for fav_car in self.fav_cars if fav_car['ID'] != car_id]

    # Check whether a car is already in the favorites list.
    def is_favorite(self, car_id):
        return any(fav_car['ID'] == car_id for fav_car in self.fav_cars)

    # Method to return a list of favorite cars that still exist in the catalog.
    def get_favorites(self):
        return [fav_car for fav_car in self.fav_cars if self.if_exist(fav_car['ID'])]
    
    ### Admin-only functions for modifying the catalog

    # Method to remove a car from the catalog only if the user authenticates as an admin.
    def remove_from_catalogue(self, id):
        username = input("What is your username?\n")
        password = input("What is your password?\n")

        try:
            # Open the admin credentials file.
            with open("admins.csv", mode="r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    # Check if the credentials match an admin account.
                    if (row[0] == username and row[2] == password):
                        # If authenticated, look for the car in the catalog.
                        for item in self.catalog:
                            if item["ID"] == id:
                                self.catalog.remove(item)
                                print(f"Item with ID {id} removed successfully.")
                                return
                print("Authentication failed or admin not found.")
        except FileNotFoundError:
            print("There's no admin file found. Please check again.")

    # Method to add a new car to the catalog (CSV file) after admin authentication.
    def add_to_catalogue(self, id, make, model, year, color, video):
        username = input("What is your username?\n")
        password = input("What is your password?\n")

        try:
            # Verify admin credentials.
            with open("admins.csv", mode="r", newline="") as admin_file:
                reader = csv.reader(admin_file)
                for row in reader:
                    if (row[0] == username and row[2] == password):
                        # If authenticated, append the new car data to the CSV.
                        with open("database.csv", mode="a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow([id, make, model, year, color, video])
                        print("Item added to catalog successfully.")
                        return
                print("Authentication failed or admin not found.")
        except FileNotFoundError:
            print("There's no admin file found. Please check again.")

# The following commented-out sections are test code examples that demonstrate how the admin functions could be used.
# They simulate adding and removing cars from the catalog and verify changes by reading the CSV file.

# # Setup test admin accounts
# with open("admins.csv", "w") as f:
#     f.write("admin1,admin1@dealership.com,secure123\n")
#     f.write("manager1,manager@dealership.com,manage456\n")

# # Test 1: Admin adds a car successfully
# print("\nTest 1: Admin adds new car")
# # Mock admin login inputs
# admin_username = "admin1"
# admin_password = "secure123"

# print(f"Attempting login as {admin_username}...")
# # In real code this would be input() prompts
# new_car = {
#     "ID": "201",
#     "Make": "Tesla", 
#     "Model": "Model 3",
#     "Year": "2023",
#     "Color": "White"
# }

# if admin_username == "admin1" and admin_password == "secure123":
#     print("Admin authenticated")
#     print(f"Adding {new_car['Make']} {new_car['Model']} to catalog...")
#     with open("catalog.csv", "a") as f:
#         f.write(f"{new_car['ID']},{new_car['Make']},{new_car['Model']}," 
#                 f"{new_car['Year']},{new_car['Color']}\n")
#     print("Car added successfully")
# else:
#     print("Admin authentication failed")

# # Test 2: Non-admin tries to add car
# print("\nTest 2: Regular user fails to add car")
# regular_user = "sales1"
# regular_pass = "sales789"

# print(f"Attempting login as {regular_user}...")
# if regular_user in ["admin1", "manager1"]:
#     print("This should never happen - regular user got admin access!")
# else:
#     print("Regular user correctly blocked from adding cars")

# # Test 3: Admin removes a car
# print("\nTest 3: Admin removes car")
# car_to_remove = "201"

# print(f"Attempting to remove car ID {car_to_remove}...")
# if admin_username == "admin1":
#     print("Admin authenticated")
#     with open("catalog.csv", "r") as f:
#         cars = [line for line in f if not line.startswith(car_to_remove)]
#     with open("catalog.csv", "w") as f:
#         f.writelines(cars)
#     print(f"Removed car ID {car_to_remove}")
# else:
#     print("Admin authentication failed")

# # Test 4: Verify changes
# print("\nFinal verification:")
# try:
#     with open("catalog.csv", "r") as f:
#         print("Current catalog:")
#         for line in f:
#             print(line.strip())
# except FileNotFoundError:
#     print("No catalog file found (everything was removed)")

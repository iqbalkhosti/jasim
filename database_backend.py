import csv

class Database:

    car_catalog = [] # list for storing all information about cars
    categories = [] # list for storing all possible categories
    fav_cars = [] # list for storing favourite cars of users

    # constructor
    def __init__(self):
        with open("database.csv", "r") as file:
            reader = csv.DictReader(file)
            self.catalog = [row for row in reader]
            self.categories = reader.fieldnames

    # add a new car to the catalog
    def add_car(self, car_info):
        if not car_info["Year"].isdigit():
            print("Invalid Year. Year must be a number.")
            return
        print("For bulk adding, please edit CSV directly") #$
        self.catalog.append(car_info)

    # update an existing car
    def update_car(self, car_info):
        for item in self.catalog:
            if item["ID"] == car_info["ID"]:
                item.update(car_info)
                break

    # remove an existing car
    def remove_car(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                self.catalog.remove(item)
                break

    # checks if a specific ID exists
    def if_exist(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                return True
        return False

    # saves the catalog back to the csv
    def save_catalog(self):
        with open("database.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.categories)
            writer.writeheader()
            writer.writerows(self.catalog)

    # used for filtering specific items
    def search(self, terms, text):
        terms = terms + text.strip().lower().split()
        results = [item for item in self.get_car_catalog() if all(any(term in str(item[category]).lower() for category in self.get_categories()) for term in terms)] if terms else self.get_car_catalog()
        return results

    # catalog getter
    def get_car_catalog(self):
        return self.catalog
    
    # categories getter
    def get_categories(self):
        return self.categories
    
    # car getter
    def get_car(self, ID):
        for item in self.catalog:
            if item["ID"] == ID:
                return item
        return None
    
  #  FOR NOW, THIS IS HERE. WE MAY WANT TO MOVE THIS TO A NEW CLASS HOWEVER
    def save_fav_car(self, make, model, year, color):
        for i in self.catalog:
            if(i.get("Make")==make and i.get("Model")==model and i.get("Year")==str(year) and i.get("Color")==color):
                
                self.fav_cars.append(i)


# This function goes through the list of fav cars and then check for the attribute mentioned in the first arugement of the function
# And if it finds the value matching with the attribute in the arugement it will add the whole dictionary element to the list and after 
# checking the whole list of fav_cars and making sure every car with the attribute is added to the filtered list, then it returns the filtered list
                
# NEEDS TO BE TESTED #

    def filter_fav_cars(self, input2):
        self.filtered_list = []

        for d in self.fav_cars:
            for value in d.values():
                if input2 in value:
                    self.filtered_list.append(d)

        return self.filtered_list


# Testing code

# d1 = Database()
# d1.save_fav_car("Honda", "Civic", "2019", "Blue")
# d1.save_fav_car("Honda", "Accord", "2011", "Gray")



# print(d1.filter_fav_cars("Model", "Honda"))

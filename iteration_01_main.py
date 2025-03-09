import csv

'''
Prints only appear in the console, as such they are not really part of the program.
Please mark prints you want to be part of the program with a '$'

PLEASE FORMAT EVERYTHING AS STRINGS WHEN POSSIBLE
THE DICTIONARY OR CATALOG DEALS ENTIRELY IN STRINGS
'''

#automaticelly downloads the database as dictionary <catalog>, saved categories as <categories>
with open("database.csv", "r") as file:
    reader = csv.DictReader(file)
    catalog = [row for row in reader]
    categories = reader.fieldnames

# save catalog as csv
def save_catalog():
    with open("database.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=categories)
        writer.writeheader()
        writer.writerows(catalog)

def add_car(car_info):
    print("For bulk adding, please edit CSV directly") #$
    catalog.append(car_info)

def update_car(car_info):
    for item in catalog:
        if item["ID"] == car_info["ID"]:
            item.update(car_info)
            return

def remove_car(ID):
    found = False
    for item in catalog:
        if item["ID"] == ID:
            catalog.remove(item)
            found = True
            break  # Exit the loop once the item is found and removed
    if not found:
        print("This item does not exist.") #$
        
def if_exist(ID):
    for item in catalog:
        if item["ID"] == ID:
            print("ID already exists.")
            return True
    print("ID does not exist.")
    return False

'''
Filters is a hashmap each filter with the keyword as a parameter
Gets all different categories in filters, compares them by keypair individually to each item
'''
def find_match_items(filters):
    items = []
    filter_keys = filters.keys()
    for item in catalog:
        match = True
        for key in filter_keys:
            if not item.get(key) == filters.get(key):
                match = False
                break
        if(match):
            items.append(item)
    return items

fav_cars =[]

def save_fav_car(make, model, year, color):
    
    for i in catalog:
        if(i.get("Make")==make and i.get("Model")==model and i.get("Year")==str(year) and i.get("Color")==color):
            
            fav_cars.append(i)
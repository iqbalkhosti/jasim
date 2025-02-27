import csv

'''
Prints only appear in the console, as such they are not really part of the program.
Please mark prints you want to be part of the program with a '$'
'''

#automaticelly downloads the database as dictionary <catalog>, saved categories as <categories>
with open("database.csv", "r") as file:
    reader = csv.DictReader(file)
    catalog = [row for row in reader]
    categories = reader.fieldnames

def add_car(car_info):
    print("For bulk adding, please edit CSV directly") #$
    catalog.append(car_info)

def remove_car(ID):
    for item in catalog:
        if item["ID"] == ID:
            del item
        else:
            print("This item does not exist.")
        
def if_exist(ID):
    for item in catalog:
        if item["ID"] == ID:
            print("ID already exists.")
            return True
    print("ID does not exist.")
    return False
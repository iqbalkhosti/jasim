# task 9: User's favourite car is added to list of dictionaries where they can save it and loop through it
# Task 9

# *** Needs to be tested **** #

# Assuming that the catalog is gonna be imported to this file 

fav_cars =[]

def save_fav_car(make, model, year, color):
    
    for i in catalog:
        if(i.get("Make")==make and i.get("Model")==model and i.get("Year")==str(year) and i.get("Color")==color):
            
            fav_cars.append(i)
    

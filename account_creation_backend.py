# This page will be dedicated to code specific to Account creation, for now we will be using a CSV file to store the user sign up information
# And could use them later for to be used for sign in

import csv
import json

## I created the two conditions in there becaise it will determine where to save what
## Even though I could create a column in the CSV users file I still want to have two separate files both for distincting the 
## account types, but as well as it will be more flexible to just see the admins, rather than going through list of a bunch of Users 
## And checking which accounts are admin and which are not, specifically if its a CSV file

def register_user(username, email, password, account_type):
    if(account_type.lower() != "admin"):
        with open("users.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, email, password])

    if(account_type.lower() == "admin"):
        with open("admins.csv", mode="a",newline="") as admin_file:
            writer = csv.writer(admin_file)
            writer.writerow([username, email, password])

def add_to_wishlist(username, wishlist_item):
   
    with open("wishlists.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        
        wishlist_item_str = json.dumps(wishlist_item)

        writer.writerow([username, wishlist_item_str])
    print(f"Added {wishlist_item} to {username}'s wishlist.")

def get_wishlist(username):
    wishlist = []
    try:
        with open("wishlists.csv", mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == username:
                    # Convert the JSON string back to a dictionary
                    wishlist_item = json.loads(row[1])
                    wishlist.append(wishlist_item)
    except FileNotFoundError:
        print("No wishlist file found. It may be the first time you're running this.")
    return wishlist


### Here are some specific functionalities that only the admin account will be able to have, and those will be as below,
### These functionalities can only be accessed if the account type is admin
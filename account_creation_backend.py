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

# Test 1: Register regular users and admins
print("=== Testing User Registration ===")
register_user("john_doe", "john@example.com", "password123", "user")
register_user("jane_smith", "jane@example.com", "securepass", "user")
register_user("admin_alice", "alice@admin.com", "adminpass", "admin")
register_user("admin_bob", "bob@admin.com", "rootpass", "ADMIN")  # Test case insensitivity
print("User registration completed. Check users.csv and admins.csv files.\n")

# Test 2: Add items to wishlists
print("=== Testing Wishlist Functionality ===")
# Add items to John's wishlist
add_to_wishlist("john_doe", {"item": "Book", "title": "Python Programming", "price": 39.99})
add_to_wishlist("john_doe", {"item": "Headphones", "brand": "Sony", "price": 199.99})

# Add items to Jane's wishlist
add_to_wishlist("jane_smith", {"item": "Laptop", "model": "MacBook Pro", "price": 1499.99})
add_to_wishlist("jane_smith", {"item": "Phone", "model": "iPhone 15", "price": 999.99})

# Add to admin's wishlist (should work the same way)
add_to_wishlist("admin_alice", {"item": "Desk", "type": "Standing Desk", "price": 399.99})
print("\n")

# Test 3: Retrieve wishlists
print("=== Testing Wishlist Retrieval ===")
print("John's wishlist:", get_wishlist("john_doe"))
print("Jane's wishlist:", get_wishlist("jane_smith"))
print("Alice's wishlist:", get_wishlist("admin_alice"))
print("Non-existent user's wishlist:", get_wishlist("nonexistent_user"))
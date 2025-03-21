# This page will be dedicated to code specific to Account creation, for now we will be using a CSV file to store the user sign up information
# And could use them later for to be used for sign in




def register_user(username, email, password):
    with open("users.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, email, password])


def add_to_wishlist(username, wishlist_item):
   
    with open("wishlists.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        # Convert the dictionary to a JSON string
        wishlist_item_str = json.dumps(wishlist_item)
        # Write the username and the JSON string representation of the item
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



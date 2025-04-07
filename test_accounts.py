import unittest
import os
import csv
import json
from account_creation_backend import register_user, add_to_wishlist, get_wishlist

class TestAccountManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.users_file = "users.csv"
        cls.admins_file = "admins.csv"
        cls.wishlist_file = "wishlists.csv"
        
        cls.backup_files = {}
        for f in [cls.users_file, cls.admins_file, cls.wishlist_file]:
            if os.path.exists(f):
                with open(f, 'r') as original:
                    cls.backup_files[f] = original.read()

    def setUp(self):
        for f in [self.users_file, self.admins_file, self.wishlist_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_register_regular_user(self):
        register_user("test_user", "user@test.com", "password123", "user")
        
        with open(self.users_file, "r") as f:
            users = list(csv.reader(f))
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0], ["test_user", "user@test.com", "password123"])

    def test_register_admin_user(self):
        register_user("test_admin", "admin@test.com", "admin123", "admin")
        
        with open(self.admins_file, "r") as f:
            admins = list(csv.reader(f))
            self.assertEqual(len(admins), 1)
            self.assertEqual(admins[0], ["test_admin", "admin@test.com", "admin123"])

    def test_case_insensitive_account_type(self):
        register_user("test_admin2", "admin2@test.com", "admin456", "ADMIN")
        
        with open(self.admins_file, "r") as f:
            admins = list(csv.reader(f))
            self.assertEqual(len(admins), 1) 

    def test_add_to_wishlist(self):
        test_item = {"ID": "9", "Make": "Tesla", "Model": "Model 3", "Year": "2020", "Color": "Blue"}
        add_to_wishlist("test_user", test_item)
        
        with open(self.wishlist_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "test_user")
            self.assertEqual(json.loads(rows[0][1]), test_item)

    def test_get_wishlist(self):
        test_items = [
            {"ID": "9", "Make": "Tesla", "Model": "Model 3", "Year": "2020", "Color": "Blue"},
            {"ID": "10", "Make": "Ford", "Model": "Mustang", "Year": "2021", "Color": "Red"}
        ]
        
        with open(self.wishlist_file, "w", newline="") as f:
            writer = csv.writer(f)
            for item in test_items:
                writer.writerow(["test_user", json.dumps(item)])
        
        wishlist = get_wishlist("test_user")
        self.assertEqual(len(wishlist), 2)  
        self.assertEqual(wishlist, test_items)

    def test_get_empty_wishlist(self):
        wishlist = get_wishlist("nonexistent_user")
        self.assertEqual(wishlist, [])

    @classmethod
    def tearDownClass(cls):
        for f, content in cls.backup_files.items():
            if content:
                with open(f, 'w') as original:
                    original.write(content)
            elif os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    unittest.main()
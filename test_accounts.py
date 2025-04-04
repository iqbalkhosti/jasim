import unittest
import os
import csv
import json

# Import from your actual account management file
from account_creation_backend import register_user, add_to_wishlist, get_wishlist

class TestAccountManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use the same filenames as your implementation
        cls.users_file = "users.csv"
        cls.admins_file = "admins.csv"
        cls.wishlist_file = "wishlists.csv"
        
        # Backup any existing files
        cls.backup_files = {}
        for f in [cls.users_file, cls.admins_file, cls.wishlist_file]:
            if os.path.exists(f):
                with open(f, 'r') as original:
                    cls.backup_files[f] = original.read()
            else:
                cls.backup_files[f] = None

    def setUp(self):
        # Clear test files before each test
        for f in [self.users_file, self.admins_file, self.wishlist_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_register_regular_user(self):
        register_user("test_user", "user@test.com", "password123", "user")
        
        # Verify
        with open(self.users_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0].strip(), "test_user,user@test.com,password123")

    def test_register_admin_user(self):
        register_user("test_admin", "admin@test.com", "admin123", "admin")
        
        # Verify
        with open(self.admins_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0].strip(), "test_admin,admin@test.com,admin123")

    def test_case_insensitive_account_type(self):
        register_user("test_admin2", "admin2@test.com", "admin456", "ADMIN")
        
        # Should still go to admins.csv
        with open(self.admins_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)

    def test_add_to_wishlist(self):
        test_item = {"product": "Car", "model": "Tesla Model S"}
        add_to_wishlist("test_user", test_item)
        
        # Verify
        with open(self.wishlist_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "test_user")
            self.assertEqual(json.loads(rows[0][1]), test_item)

    def test_get_wishlist(self):
        # Setup test data
        test_items = [
            {"product": "Car", "model": "Tesla Model S"},
            {"product": "Accessory", "name": "Charger"}
        ]
        
        # Add to wishlist file directly
        with open(self.wishlist_file, "w", newline="") as f:
            writer = csv.writer(f)
            for item in test_items:
                writer.writerow(["test_user", json.dumps(item)])
        
        # Test retrieval
        wishlist = get_wishlist("test_user")
        self.assertEqual(len(wishlist), 2)
        self.assertEqual(wishlist, test_items)

    def test_get_empty_wishlist(self):
        wishlist = get_wishlist("nonexistent_user")
        self.assertEqual(wishlist, [])

    @classmethod
    def tearDownClass(cls):
        # Restore original files
        for f, content in cls.backup_files.items():
            if content is not None:
                with open(f, 'w') as original:
                    original.write(content)
            elif os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    unittest.main()
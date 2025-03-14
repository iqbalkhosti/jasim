import unittest
import csv
import os
from database_backend import Database

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a temporary CSV file for testing
        cls.test_csv = "test_database.csv"
        with open(cls.test_csv, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "Make", "Model", "Year", "Color"])
            writer.writeheader()
            writer.writerow({"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"})
            writer.writerow({"ID": "2", "Make": "Honda", "Model": "Civic", "Year": "2019", "Color": "Blue"})

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary CSV file after testing
        os.remove(cls.test_csv)

    def setUp(self):
        # Initialize the Database with the test CSV file
        self.db = Database()
        self.db.catalog = []
        with open(self.test_csv, "r") as file:
            reader = csv.DictReader(file)
            self.db.catalog = [row for row in reader]
            self.db.categories = reader.fieldnames

    def test_add_car(self):
        new_car = {"ID": "3", "Make": "Ford", "Model": "Mustang", "Year": "2021", "Color": "Black"}
        self.db.add_car(new_car)
        self.assertIn(new_car, self.db.catalog)

    def test_update_car(self):
        updated_car = {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2021", "Color": "Red"}
        self.db.update_car(updated_car)
        self.assertEqual(self.db.get_car("1"), updated_car)

    def test_remove_car(self):
        self.db.remove_car("1")
        self.assertNotIn({"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"}, self.db.catalog)

    def test_if_exist(self):
        self.assertTrue(self.db.if_exist("1"))
        self.assertFalse(self.db.if_exist("999"))

    def test_search(self):
        results = self.db.search([], "Toyota")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["Make"], "Toyota")

    def test_get_car(self):
        car = self.db.get_car("1")
        self.assertEqual(car["Make"], "Toyota")
        self.assertEqual(car["Model"], "Corolla")

    def test_save_catalog(self):
        self.db.save_catalog()
        with open(self.test_csv, "r") as file:
            reader = csv.DictReader(file)
            saved_catalog = [row for row in reader]
        self.assertEqual(saved_catalog, self.db.catalog)

    def test_add_car_invalid_year(self):
        new_car = {"ID": "5", "Make": "Tesla", "Model": "Model S", "Year": "Twenty Twenty", "Color": "Red"}
        self.db.add_car(new_car)
        self.assertNotIn(new_car, self.db.catalog)

    def test_add_car_missing_fields(self):
        new_car = {"ID": "4", "Make": "", "Model": "", "Year": "", "Color": ""}
        self.db.add_car(new_car)
        self.assertNotIn(new_car, self.db.catalog) 

if __name__ == "__main__":
    unittest.main()
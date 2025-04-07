import unittest
import csv
import os
from database_backend import Database

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_csv = "test_database.csv"
        with open(cls.test_csv, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "Make", "Model", "Year", "Color"])
            writer.writeheader()
            writer.writerow({"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"})
            writer.writerow({"ID": "2", "Make": "Honda", "Model": "Civic", "Year": "2019", "Color": "Blue"})

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_csv)

    def setUp(self):
        self.db = Database()
        with open(self.test_csv, "r") as file:
            reader = csv.DictReader(file)
            self.db.catalog = [row for row in reader]
            self.db.categories = reader.fieldnames

    def test_add_car_invalid_year(self):
        bad_car = {"ID": "5", "Make": "Tesla", "Model": "Model S", "Year": "Twenty Twenty", "Color": "Red"}
        self.db.add_car(bad_car)
        self.assertNotIn(bad_car, self.db.catalog)

    def test_add_car_missing_fields(self):
        bad_car = {"ID": "4", "Make": "", "Model": "", "Year": "", "Color": ""}
        self.db.add_car(bad_car)
        self.assertNotIn(bad_car, self.db.catalog)

    def test_add_car(self):
        car = {"ID": "3", "Make": "Ford", "Model": "Mustang", "Year": "2021", "Color": "Black"}
        self.db.add_car(car)
        self.assertIn(car, self.db.catalog)

    def test_update_car(self):
        updated = {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2021", "Color": "Red"}
        self.db.update_car(updated)
        self.assertEqual(self.db.get_car("1"), updated)

    def test_remove_car(self):
        self.db.remove_car("1")
        self.assertIsNone(self.db.get_car("1"))

    def test_if_exist(self):
        self.assertTrue(self.db.if_exist("1"))
        self.assertFalse(self.db.if_exist("999"))

    def test_get_car(self):
        car = self.db.get_car("1")
        self.assertEqual(car["Make"], "Toyota")
        self.assertEqual(car["Model"], "Corolla")

    def test_save_catalog(self):
        self.db.save_catalog()
        with open(self.test_csv, "r") as file:
            reader = csv.DictReader(file)
            saved = [row for row in reader]
        self.assertEqual(saved, self.db.catalog)

    def test_search_exact_match(self):
        results = self.db.search("Toyota Corolla 2020 Red".split())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ID"], "1")

    def test_search_partial_match(self):
        results = self.db.search("Toyota Corolla".split())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ID"], "1")

    def test_search_no_match(self):
        results = self.db.search("Tesla Model S".split())
        self.assertEqual(len(results), 0)

    def test_search_relevance_based(self):
        results = self.db.search("Toyota Blue".split(), relevance=True)
        self.assertEqual(len(results), 2)

    def test_search_empty_input(self):
        results = self.db.search("".split())
        self.assertEqual(len(results), 2)

    def test_search_case_insensitivity(self):
        results = self.db.search("toyota corolla".split())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ID"], "1")

    def test_search_multiple_terms(self):
        results = self.db.search("Honda Civic Blue".split())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ID"], "2")

    def test_filter_fav_cars(self):
        self.db.fav_cars = [
            {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"},
            {"ID": "2", "Make": "Honda", "Model": "Civic", "Year": "2019", "Color": "Blue"},
            {"ID": "3", "Make": "Ford", "Model": "Mustang", "Year": "2021", "Color": "Black"}
        ]
        self.assertEqual(len(self.db.filter_fav_cars("Toyota")), 1)
        self.assertEqual(len(self.db.filter_fav_cars("Blue")), 1)
        self.assertEqual(len(self.db.filter_fav_cars("2021")), 1)
        self.assertEqual(len(self.db.filter_fav_cars("Green")), 0)

if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import MagicMock, patch
from tkinter import Tk, ttk
import tkinter as tk
from frontend import CatalogApp

class TestCatalogApp(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.app = CatalogApp(self.root)

    def tearDown(self):
        self.root.destroy()

# This is commented out until we have an actual use for the login screen and not just a placeholder
    # @patch('tkinter.messagebox.showerror')
    # def test_login_screen_failure(self, mock_showerror):
    #     self.app.login_screen()
    #     self.app.main_menu = MagicMock()
    #     self.app.login_screen()
    #     self.app.main_menu.assert_not_called()
    #     mock_showerror.assert_called_once_with("Login Failed", "Invalid username or password")

    # @patch('tkinter.messagebox.showerror')
    # def test_login_screen_success(self, mock_showerror):
    #     self.app.login_screen()
    #     self.app.main_menu = MagicMock()
    #     self.app.login_screen()
    #     self.app.main_menu.assert_not_called()
    #     mock_showerror.assert_called_once_with("Login Failed", "Invalid username or password")

    @patch('tkinter.simpledialog.askstring')
    def test_view_item(self, mock_askstring):
        mock_askstring.return_value = "1"
        self.app.DB.get_car = MagicMock(return_value={"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"})
        self.app.display_item_details = MagicMock()
        self.app.view_item()
        # Verify that display_item_details is called with the correct item
        self.app.display_item_details.assert_called_once_with({"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"})

    @patch('tkinter.messagebox.showerror')
    def test_send_info(self, mock_showerror):
        self.app.DB.get_car_catalog = MagicMock(return_value=[{"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"}])
        self.app.DB.add_car = MagicMock()
        self.app.main_menu = MagicMock()
        entries = [MagicMock(get=MagicMock(return_value="")) for _ in range(4)]
        self.app.send_info(entries)
        # Verify that showerror is called for invalid input
        mock_showerror.assert_called_once_with("Error", "Either missing Model or incorrect Year")
        # Verify that add_car and main_menu are not called
        self.app.DB.add_car.assert_not_called()
        self.app.main_menu.assert_not_called()

    def test_main_menu(self):
        self.app.main_menu()
        # Verify that the search bar and dropdown menu are displayed
        search_frame = self.app.root.winfo_children()[0]
        self.assertIsInstance(search_frame, tk.Frame)
        dropdown = search_frame.winfo_children()[-1]
        self.assertIsInstance(dropdown, ttk.Combobox)

    @patch('frontend.CatalogApp.display_item_details')
    def test_display_results(self, mock_display_item_details):
        results = [
            {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"},
            {"ID": "2", "Make": "Honda", "Model": "Civic", "Year": "2019", "Color": "Blue"}
        ]
        self.app.display_results(results)
        # Verify that the results are displayed as buttons
        frame = self.app.root.winfo_children()[0]
        buttons = [child for child in frame.winfo_children() if isinstance(child, tk.Button)]
        self.assertEqual(len(buttons), len(results) + 1)  # +1 for the "Back" button

    @patch('frontend.messagebox.showerror')
    def test_add_item(self, mock_showerror):
        self.app.DB.get_car_catalog = MagicMock(return_value=[{"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"}])
        self.app.DB.add_car = MagicMock()
        self.app.main_menu = MagicMock()

        self.app.add_item()
        entries = [
            MagicMock(get=MagicMock(return_value="Valid")),  # Make
            MagicMock(get=MagicMock(return_value="Valid")),  # Model
            MagicMock(get=MagicMock(return_value="2023")),   # Year
            MagicMock(get=MagicMock(return_value="Valid"))   # Color
        ]        
        self.app.send_info(entries)
        # Verify that the car was added and main_menu was called
        self.app.DB.add_car.assert_called_once()
        self.app.main_menu.assert_called_once()
        # Verify that showerror was not called
        mock_showerror.assert_not_called()

    @patch('frontend.messagebox.askyesno', return_value=True)
    @patch('frontend.messagebox.showinfo')
    def test_remove_item(self, mock_showinfo, mock_askyesno):
        self.app.DB.if_exist = MagicMock(return_value=True)
        self.app.DB.remove_car = MagicMock()
        self.app.main_menu = MagicMock()

        self.app.remove_item("1")
        # Verify that the car was removed and main_menu was called
        self.app.DB.remove_car.assert_called_once_with("1")
        mock_showinfo.assert_called_once_with("Success", "Car removed successfully")
        self.app.main_menu.assert_called_once()

    def test_search(self):
        self.app.search_entry = MagicMock()
        self.app.search_entry.get.return_value = "Toyota"
        self.app.terms = []

        self.app.DB.search = MagicMock(return_value=[
            {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"}
        ])
        self.app.display_results = MagicMock()

        self.app.search(True)
        # Verify that display_results was called with the correct results
        self.app.display_results.assert_called_once_with([
            {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"}
        ])

    @patch('frontend.CatalogApp.display_results')
    def test_handle_dropdown_selection_display_catalog(self, mock_display_results):
        self.app.selected_option = MagicMock()
        self.app.selected_option.get.return_value = "Display Catalog"

        # Mock the database method
        self.app.DB.get_car_catalog = MagicMock(return_value=[
            {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"}
        ])

        self.app.handle_dropdown_selection(None)
        # Verify that display_results was called with the catalog
        mock_display_results.assert_called_once_with([
            {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"}
        ])

    @patch('frontend.messagebox.showerror')
    def test_update_item(self, mock_showerror):
        self.app.DB.get_car = MagicMock(return_value={"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red"})
        self.app.DB.update_car = MagicMock()
        self.app.main_menu = MagicMock()

        self.app.update_item("1")
        entries = [
            MagicMock(get=MagicMock(return_value="Toyota")),  # Make
            MagicMock(get=MagicMock(return_value="Corolla")),  # Model
            MagicMock(get=MagicMock(return_value="2021")),     # Year
            MagicMock(get=MagicMock(return_value="Blue"))      # Color
        ]
        self.app.send_info(entries, "1")
        # Verify that the car was updated and main_menu was called
        self.app.DB.update_car.assert_called_once_with({
            "ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2021", "Color": "Blue"
        })
        self.app.main_menu.assert_called_once()
        # Verify that showerror was not called
        mock_showerror.assert_not_called()

    @patch('frontend.messagebox.showinfo')
    def test_on_save(self, mock_showinfo):
        self.app.DB.save_catalog = MagicMock()

        self.app.on_save()
        # Verify that the catalog was saved and a success message was shown
        self.app.DB.save_catalog.assert_called_once()
        mock_showinfo.assert_called_once_with("Success", "Catalog saved successfully")

    @patch('frontend.messagebox.askyesno', return_value=True)
    @patch('frontend.CatalogApp.on_save')
    def test_on_closing_save(self, mock_on_save, mock_askyesno):
        self.app.root.destroy = MagicMock()

        self.app.on_closing()
        # Verify that the user was prompted and the catalog was saved
        mock_askyesno.assert_called_once_with("Save Catalog", "Would you like to save the catalog before exiting?")
        mock_on_save.assert_called_once()
        self.app.root.destroy.assert_called_once()

    @patch('frontend.TkinterVideo')
    def test_display_item_details(self, mock_video_player):
        item = {
            "ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red",
            "Video": "path/to/video.mp4"
        }
        self.app.display_item_details(item)
        # Verify that the video player was initialized
        mock_video_player.assert_called_once()
        mock_video_player.return_value.load.assert_called_once_with("path/to/video.mp4")
        mock_video_player.return_value.play.assert_called_once()

    # @patch('tkinter.messagebox.showinfo')
    # def test_logout(self, mock_showinfo):
    #     self.app.clear_window = MagicMock()
    #     self.app.login_screen = MagicMock()
        
    #     self.app.logout()
        
    #     # Verify that clear_window was called
    #     self.app.clear_window.assert_called_once()
        
    #     # Verify that login_screen was called
    #     self.app.login_screen.assert_called_once()
        
    #     # Verify that showinfo was called with the correct arguments
    #     mock_showinfo.assert_called_once_with("Logout Successful", "You have been logged out.")

if __name__ == "__main__":
    unittest.main()
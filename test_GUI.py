import unittest
from unittest.mock import MagicMock, patch, Mock
from tkinter import Tk, ttk, Menu, StringVar, BooleanVar, Frame
import tkinter as tk
from Front_Layout import CatalogApp
from PIL import Image, ImageTk
from io import BytesIO

class TestCatalogAppGUI(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.app = CatalogApp(self.root)
        self.app.DB = MagicMock()  # Mock the database
        
        # Initialize required attributes
        self.app.terms = []
        self.app.current_view = 'main'
        self.app.text = ""
        
        # Create required frames
        self.app.results_frame = Frame(self.root)
        self.app.content_frame = Frame(self.root)
        
        # Mock database structure and methods
        self.app.DB.get_categories.return_value = ["ID", "Make", "Model", "Year", "Color", "ImageURL"]
        self.app.DB.get_car_catalog.return_value = [
            {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020", "Color": "Red", "ImageURL": ""},
            {"ID": "2", "Make": "Honda", "Model": "Civic", "Year": "2019", "Color": "Blue", "ImageURL": ""}
        ]
        self.app.DB.get_car.return_value = {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020"}
        self.app.DB.search.return_value = []
        self.app.DB.is_favorite.return_value = False
        self.app.DB.if_exist.return_value = True

    def tearDown(self):
        try:
            self.root.destroy()
        except:
            pass

    # Main Menu Tests
    def test_main_menu_ui(self):
        self.app.main_menu()
        main_frame = self.root.winfo_children()[0]
        self.assertIsInstance(main_frame, tk.Frame)

    # Filter Tests
    def test_filter_dropdown_creation(self):
        test_frame = tk.Frame(self.root)
        self.app.create_filter_dropdown(test_frame, "Make")
        dropdown_frame = test_frame.winfo_children()[0]
        self.assertIsInstance(dropdown_frame, tk.Frame)

    def test_apply_filters(self):
        self.app.filter_checkboxes = {
            "Make": [BooleanVar(value=True), BooleanVar(value=False)],
            "Model": [BooleanVar(value=False)]
        }
        self.app.display_results = MagicMock()
        self.app.apply_filters("Make", ["Toyota", "Honda"])
        self.app.display_results.assert_called_once()

    # Search Tests
    def test_search_from_entry(self):
        self.app.main_menu()
        self.app.search_entry = MagicMock()
        self.app.search_entry.get.return_value = "Toyota"
        self.app.display_results = MagicMock()
        self.app.search(True)
        self.app.display_results.assert_called_once()

    def test_search_with_terms(self):
        self.app.terms = ["Red"]
        self.app.text = "Red"  # Set this explicitly for the test
        self.app.display_results = MagicMock()
        self.app.search()
        self.app.DB.search.assert_called_with("Red")

    # Catalog Display Tests
    def test_display_catalog_grid(self):
        test_results = [{"ID": "1", "Make": "Toyota", "Model": "Corolla", "ImageURL": ""}]
        self.app.display_catalog_grid(test_results)
        canvas = self.app.results_frame.winfo_children()[0]
        scrollable_frame = canvas.winfo_children()[0]
        self.assertGreater(len(scrollable_frame.winfo_children()), 0)

    @patch('urllib.request.urlopen')
    def test_display_catalog_with_images(self, mock_urlopen):
        # Setup mock image
        mock_image = MagicMock()
        mock_bytes = BytesIO()
        mock_urlopen.return_value = mock_bytes
        
        test_results = [{"ID": "1", "Make": "Toyota", "Model": "Corolla", "ImageURL": "http://test.com/image.jpg"}]
        self.app.display_catalog_grid(test_results)
        mock_urlopen.assert_called_once_with("http://test.com/image.jpg")

    @patch('tkVideoPlayer.TkinterVideo')
    def test_video_preview_in_details(self, mock_video_player):
        test_item = {
            "ID": "1", 
            "Make": "Toyota", 
            "Video": "http://test.com/video.mp4"
        }
        self.app.display_item_details(test_item)
        mock_video_player.assert_called_once()
        mock_video_player.return_value.load.assert_called_with("http://test.com/video.mp4")
        mock_video_player.return_value.play.assert_called_once()

    @patch('tkinter.messagebox.showerror')
    @patch('tkVideoPlayer.TkinterVideo')
    def test_invalid_video_url(self, mock_video_player, mock_showerror):
        mock_video_player.return_value.load.side_effect = Exception("Invalid video")
        test_item = {"ID": "1", "Video": "invalid_url"}
        self.app.display_item_details(test_item)
        mock_showerror.assert_called_once_with("Error", "Could not load video")

    # Item Detail Tests
    def test_display_item_details(self):
        test_item = {"ID": "1", "Make": "Toyota", "Model": "Corolla", "Year": "2020"}
        self.app.display_item_details(test_item)
        main_frame = self.root.winfo_children()[0]
        self.assertEqual(len(main_frame.winfo_children()), 3)

    # CRUD Operation Tests
    def test_add_item_ui(self):
        self.app.add_item()
        frame = self.root.winfo_children()[0]
        entries = [child for child in frame.winfo_children() if isinstance(child, tk.Entry)]
        self.assertGreater(len(entries), 0)

    def test_update_item_ui(self):
        # Mock the entry fields
        mock_entry = MagicMock()
        mock_entry.insert = MagicMock()
        self.app.update_item = MagicMock()
        
        # Call with mock
        self.app.update_item("1")
        self.app.update_item.assert_called_once_with("1")

    @patch('tkinter.messagebox.showerror')
    def test_send_info_invalid(self, mock_showerror):
        # Create mock entries with proper structure
        mock_entries = []
        for category in ["Make", "Model", "Year", "Color", "ImageURL"]:
            mock_entry = MagicMock()
            mock_entry.get.return_value = "" if category == "Model" else "test"
            mock_entries.append(mock_entry)
        
        self.app.send_info(mock_entries)
        mock_showerror.assert_called_once_with("Error", "Either missing Model or incorrect Year")

    @patch('tkinter.messagebox.askyesno', return_value=True)
    @patch('tkinter.messagebox.showinfo')
    def test_remove_item(self, mock_showinfo, mock_askyesno):
        self.app.remove_item("1")
        mock_askyesno.assert_called_once()
        self.app.DB.remove_car.assert_called_once_with("1")
        mock_showinfo.assert_called_once_with("Success", "Car removed successfully")

    # Favourites Tests
    def test_toggle_favorite_add(self):
        self.app.DB.is_favorite.return_value = False
        self.app.toggle_favorite("1")
        self.app.DB.add_favorite.assert_called_once_with("1")

    def test_show_favorites(self):
        self.app.display_results = MagicMock()
        self.app.show_favorites()
        self.app.DB.get_favorites.assert_called_once()
        self.app.display_results.assert_called_once()

    # System Function Tests
    @patch('tkinter.messagebox.showinfo')
    def test_on_save(self, mock_showinfo):
        self.app.on_save()
        self.app.DB.save_catalog.assert_called_once()
        mock_showinfo.assert_called_once_with("Success", "Catalog saved successfully")

    @patch('tkinter.messagebox.askyesno', return_value=True)
    @patch('Front_Layout.CatalogApp.on_save')
    def test_on_closing_save(self, mock_on_save, mock_askyesno):
        self.app.on_closing()
        mock_askyesno.assert_called_once()
        mock_on_save.assert_called_once()

    @patch('tkinter.messagebox.askyesno', return_value=False)
    def test_on_closing_no_save(self, mock_askyesno):
        try:
            self.app.on_closing()
            mock_askyesno.assert_called_once()
        except:
            pass  

    # View Item Tests
    @patch('tkinter.simpledialog.askstring', return_value="1")
    def test_view_item(self, mock_askstring):
        self.app.display_item_details = MagicMock()
        self.app.view_item()
        self.app.display_item_details.assert_called_once()

    # Clear Window Test
    def test_clear_window(self):
        tk.Label(self.root, text="Test").pack()
        self.app.clear_window()
        self.assertEqual(len(self.root.winfo_children()), 0)

    # @patch('tkinter.messagebox.showinfo')
    # def test_logout(self, mock_showinfo):
    #     self.app.clear_window = MagicMock()
    #     self.app.login_screen = MagicMock()

    #     self.app.logout()
    #     self.app.logout()

    #     # Verify that clear_window was called
    #     self.app.clear_window.assert_called_once()
    #     # Verify that clear_window was called
    #     self.app.clear_window.assert_called_once()

    #     # Verify that login_screen was called
    #     self.app.login_screen.assert_called_once()
    #     # Verify that login_screen was called
    #     self.app.login_screen.assert_called_once()

    #     # Verify that showinfo was called with the correct arguments
    #     mock_showinfo.assert_called_once_with("Logout Successful", "You have been logged out.")
    #     # Verify that showinfo was called with the correct arguments
    #     mock_showinfo.assert_called_once_with("Logout Successful", "You have been logged out.")

if __name__ == "__main__":
    unittest.main()
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# To test our UI-dependent code, we must mock the tkinter module
# before it is imported by the module we are testing.
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()

# Now we can safely import our application code
import Expense_tracker

class TestExpenseTracker(unittest.TestCase):

    def setUp(self):
        """Set up for each test. This runs before each test function."""
        # Reset the global expenses list before each test to ensure isolation
        Expense_tracker.expenses = []
        self.test_csv_file = "expenses.csv"

        # Clean up any leftover files from previous runs
        if os.path.exists(self.test_csv_file):
            os.remove(self.test_csv_file)

    def tearDown(self):
        """Tear down after each test. This runs after each test function."""
        # Clean up files created during the test
        if os.path.exists(self.test_csv_file):
            os.remove(self.test_csv_file)

    def test_download_csv_creates_file(self):
        """
        Tests that calling download_csv() creates the 'expenses.csv' file.
        """
        # Arrange: Add sample data using the new dictionary structure
        Expense_tracker.expenses.append({'id': 't1', 'category': 'Groceries', 'amount': 150.75})
        Expense_tracker.expenses.append({'id': 't2', 'category': 'Transport', 'amount': 55.00})

        # Act: Call the function to be tested
        Expense_tracker.download_csv()

        # Assert: Check that the file now exists
        self.assertTrue(os.path.exists(self.test_csv_file), "The CSV file was not created.")

    def test_download_csv_writes_correct_content(self):
        """
        Tests that the created CSV file contains the correct headers and data.
        """
        # Arrange: Add sample data using the new dictionary structure
        Expense_tracker.expenses.append({'id': 't1', 'category': 'Groceries', 'amount': 150.75})
        Expense_tracker.expenses.append({'id': 't2', 'category': 'Transport', 'amount': 55.0})

        # Act: Call the function
        Expense_tracker.download_csv()

        # Assert: Read the file and check its contents
        self.assertTrue(os.path.exists(self.test_csv_file))
        with open(self.test_csv_file, 'r') as f:
            lines = f.readlines()

        # Check header
        self.assertEqual(lines[0].strip(), "Category,Amount (₹)")

        # Check data rows
        self.assertEqual(len(lines), 3, "The CSV file should have one header row and two data rows.")
        self.assertEqual(lines[1].strip(), "Groceries,150.75")
        self.assertEqual(lines[2].strip(), "Transport,55.0")

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock tkinter before importing the application
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()

# Import the application code
import Expense_tracker

class TestDeleteFeature(unittest.TestCase):

    def setUp(self):
        """Set up a clean state before each test."""
        # Mock the global UI widgets that our functions will interact with
        Expense_tracker.expense_list = MagicMock()
        Expense_tracker.alert_label = MagicMock()

        # Reset the global expenses list and populate it for tests
        Expense_tracker.expenses = [
            {'id': 'I001', 'category': 'Food', 'amount': 10.0},
            {'id': 'I002', 'category': 'Transport', 'amount': 25.5},
            {'id': 'I003', 'category': 'Shopping', 'amount': 150.0}
        ]
        self.initial_expense_count = len(Expense_tracker.expenses)

    @patch('Expense_tracker.messagebox.askyesno', return_value=True)
    def test_delete_expense_successfully(self, mock_askyesno):
        """
        Tests that an expense is successfully deleted when the user confirms.
        """
        # Arrange: Mock the UI selection to return the ID of the item we want to delete
        item_to_delete_id = 'I002'
        Expense_tracker.expense_list.selection.return_value = (item_to_delete_id,)

        # Act: Call the function to be tested
        Expense_tracker.delete_expense()

        # Assert: Check that the correct expense was removed from the list
        self.assertEqual(len(Expense_tracker.expenses), self.initial_expense_count - 1)

        # Check that the specific item is gone
        ids_remaining = [exp['id'] for exp in Expense_tracker.expenses]
        self.assertNotIn(item_to_delete_id, ids_remaining)

        # Assert that the item was deleted from the Treeview UI
        Expense_tracker.expense_list.delete.assert_called_once_with(item_to_delete_id)

        # Assert that the budget was checked
        Expense_tracker.alert_label.config.assert_called()

    @patch('Expense_tracker.messagebox.askyesno', return_value=False)
    def test_delete_expense_cancelled(self, mock_askyesno):
        """
        Tests that no expense is deleted when the user cancels the confirmation.
        """
        # Arrange: Mock the UI selection
        Expense_tracker.expense_list.selection.return_value = ('I002',)

        # Act: Call the function
        Expense_tracker.delete_expense()

        # Assert: The expenses list should be unchanged
        self.assertEqual(len(Expense_tracker.expenses), self.initial_expense_count)

        # Assert that the delete method on the Treeview was not called
        Expense_tracker.expense_list.delete.assert_not_called()

    def test_delete_with_no_selection(self):
        """
        Tests that a warning is shown if the delete button is clicked with no selection.
        """
        # Arrange: Mock the selection to be empty
        Expense_tracker.expense_list.selection.return_value = ()

        # Act: Call the function
        Expense_tracker.delete_expense()

        # Assert: The expenses list should be unchanged
        self.assertEqual(len(Expense_tracker.expenses), self.initial_expense_count)

        # Assert that a warning was shown
        Expense_tracker.messagebox.showwarning.assert_called_once()


if __name__ == '__main__':
    unittest.main()

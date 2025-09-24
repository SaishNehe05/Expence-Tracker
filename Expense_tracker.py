import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import matplotlib.pyplot as plt
import numpy as np

# --- Global State ---
# These are shared between the UI and the logic functions
expenses = []
budget_limit = 0
categories = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]

# UI Widgets - these will be initialized in main()
root = None
category_var = None
amount_entry = None
expense_list = None
budget_entry = None
budget_label = None
alert_label = None

# --- Core Functions ---

def add_expense():
    category = category_var.get()
    amount = amount_entry.get()

    if not category or not amount:
        messagebox.showwarning("Input Error", "Please fill in all fields!")
        return

    try:
        amount_float = float(amount)
        # Store a unique identifier with the expense, the Treeview item ID
        item_id = expense_list.insert("", "end", values=(category, f"₹{amount_float:.2f}"))
        expenses.append({'id': item_id, 'category': category, 'amount': amount_float})
        amount_entry.delete(0, tk.END)
        check_budget()
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a valid number for amount!")

def set_budget():
    global budget_limit
    try:
        budget_limit = float(budget_entry.get())
        budget_label.config(text=f"Budget Set: ₹{budget_limit:.2f}", fg="green")
        check_budget()
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a valid number for budget!")

def check_budget():
    total_spent = sum(expense['amount'] for expense in expenses)
    if budget_limit > 0 and total_spent > budget_limit:
        alert_label.config(text="⚠️ Budget Exceeded!", fg="red")
    else:
        # To avoid showing "within limits" when no budget is set.
        if budget_limit > 0:
            alert_label.config(text="Budget is within limits", fg="blue")
        else:
            alert_label.config(text="") # Clear message if no budget

def plot_chart():
    if not expenses:
        messagebox.showinfo("No Data", "No expenses to display!")
        return

    category_totals = {cat: 0 for cat in categories}
    for expense in expenses:
        if expense['category'] in category_totals:
            category_totals[expense['category']] += expense['amount']

    # Filter out categories with no spending
    filtered_totals = {k: v for k, v in category_totals.items() if v > 0}
    if not filtered_totals:
        messagebox.showinfo("No Data", "No expenses with positive amounts to display!")
        return

    labels = list(filtered_totals.keys())
    values = list(filtered_totals.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title("Expense Distribution")
    plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

def download_csv():
    file_path = "expenses.csv"
    try:
        full_path = os.path.abspath(file_path)
        # We need to write the dictionary values, not the whole dict
        rows_to_write = [(exp['category'], exp['amount']) for exp in expenses]
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Category", "Amount (₹)"])
            writer.writerows(rows_to_write)
        messagebox.showinfo("Download Complete", f"Expenses saved to:\n{full_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file: {e}")

def edit_expense():
    """Opens a new window to edit the selected expense."""
    selected_item_id = expense_list.selection()
    if not selected_item_id:
        messagebox.showwarning("Selection Error", "Please select an expense to edit.")
        return

    item_id = selected_item_id[0]

    # Find the expense dictionary that corresponds to the item_id
    expense_to_edit = None
    for expense in expenses:
        if expense['id'] == item_id:
            expense_to_edit = expense
            break

    if not expense_to_edit:
        messagebox.showerror("Error", "Could not find the selected expense to edit.")
        return

    # Create a new Toplevel window for editing
    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Expense")
    edit_win.geometry("300x150")
    edit_win.configure(bg="#F3F1F5")

    # Create and pack widgets for the edit window
    tk.Label(edit_win, text="Category:", bg="#F3F1F5").pack(pady=(10,0))
    edit_category_var = tk.StringVar(value=expense_to_edit['category'])
    edit_category_menu = ttk.Combobox(edit_win, textvariable=edit_category_var, values=categories, state="readonly")
    edit_category_menu.pack()

    tk.Label(edit_win, text="Amount (₹):", bg="#F3F1F5").pack(pady=(10,0))
    edit_amount_var = tk.StringVar(value=str(expense_to_edit['amount']))
    edit_amount_entry = tk.Entry(edit_win, textvariable=edit_amount_var)
    edit_amount_entry.pack()

    def save_changes():
        new_category = edit_category_var.get()
        new_amount_str = edit_amount_var.get()

        if not new_category or not new_amount_str:
            messagebox.showwarning("Input Error", "Fields cannot be empty.", parent=edit_win)
            return

        try:
            new_amount = float(new_amount_str)
            # Update the original expense dictionary
            expense_to_edit['category'] = new_category
            expense_to_edit['amount'] = new_amount

            # Update the Treeview
            expense_list.item(item_id, values=(new_category, f"₹{new_amount:.2f}"))

            # Recalculate budget and close window
            check_budget()
            edit_win.destroy()
            messagebox.showinfo("Success", "Expense updated successfully.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid number for amount.", parent=edit_win)

    # Buttons for the edit window
    btn_frame = tk.Frame(edit_win, bg="#F3F1F5")
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Save", command=save_changes, bg="#4CAF50", fg="white").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", command=edit_win.destroy, bg="#F44336", fg="white").pack(side="left", padx=10)


def delete_expense():
    """Deletes the selected expense from the list."""
    selected_item = expense_list.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an expense to delete.")
        return

    # The selected_item is a tuple, we need the first element
    item_id = selected_item[0]

    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this expense?")

    if confirm:
        # Find the expense in the list by its unique ID and remove it
        global expenses
        expense_to_remove = None
        for expense in expenses:
            if expense['id'] == item_id:
                expense_to_remove = expense
                break

        if expense_to_remove:
            expenses.remove(expense_to_remove)
            expense_list.delete(item_id)
            check_budget()
            messagebox.showinfo("Success", "Expense deleted successfully.")
        else:
            messagebox.showerror("Error", "Could not find the selected expense to delete.")


# --- UI Setup ---

def main():
    global root, category_var, amount_entry, expense_list, budget_entry, budget_label, alert_label

    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("500x600")
    root.configure(bg="#F3F1F5")

    # Title
    title_label = tk.Label(root, text="Expense Tracker", font=("Arial", 18, "bold"), fg="#4A4A4A", bg="#F3F1F5")
    title_label.pack(pady=10)

    # Budget Section
    budget_frame = tk.Frame(root, bg="#E1F7D5", pady=5)
    budget_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(budget_frame, text="Set Budget:", font=("Arial", 12), bg="#E1F7D5").pack(side="left", padx=10)
    budget_entry = tk.Entry(budget_frame, width=10)
    budget_entry.pack(side="left", padx=5)
    tk.Button(budget_frame, text="Set", command=set_budget, bg="#4CAF50", fg="white").pack(side="left", padx=5)
    budget_label = tk.Label(root, text="No Budget Set", fg="red", bg="#F3F1F5")
    budget_label.pack()

    # Expense Entry
    expense_frame = tk.Frame(root, bg="#FFF", pady=5)
    expense_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(expense_frame, text="Category:", font=("Arial", 12), bg="#FFF").grid(row=0, column=0, padx=5, pady=5)
    category_var = tk.StringVar()
    category_menu = ttk.Combobox(expense_frame, textvariable=category_var, values=categories, state="readonly")
    category_menu.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(expense_frame, text="Amount (₹):", font=("Arial", 12), bg="#FFF").grid(row=1, column=0, padx=5, pady=5)
    amount_entry = tk.Entry(expense_frame, width=10)
    amount_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(expense_frame, text="Add Expense", command=add_expense, bg="#FF9800", fg="white").grid(row=2, columnspan=2, pady=5)

    # Expense List
    expense_list_frame = tk.Frame(root)
    expense_list_frame.pack(pady=5)
    columns = ("Category", "Amount")
    expense_list = ttk.Treeview(expense_list_frame, columns=columns, show="headings")
    expense_list.heading("Category", text="Category")
    expense_list.heading("Amount", text="Amount")
    expense_list.pack()

    # Action Buttons Frame
    action_buttons_frame = tk.Frame(root, bg="#F3F1F5")
    action_buttons_frame.pack(pady=5)

    # Edit and Delete Buttons
    tk.Button(action_buttons_frame, text="Edit Expense", command=edit_expense, bg="#FFC107", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(action_buttons_frame, text="Delete Expense", command=delete_expense, bg="#F44336", fg="white").grid(row=0, column=1, padx=5)


    # Alert Label
    alert_label = tk.Label(root, text="", font=("Arial", 12, "bold"), bg="#F3F1F5")
    alert_label.pack(pady=5)

    # Analysis and Download Buttons
    analysis_buttons_frame = tk.Frame(root, bg="#F3F1F5")
    analysis_buttons_frame.pack(pady=10)
    tk.Button(analysis_buttons_frame, text="View Chart", command=plot_chart, bg="#2196F3", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(analysis_buttons_frame, text="Download CSV", command=download_csv, bg="#9C27B0", fg="white").grid(row=0, column=1, padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()

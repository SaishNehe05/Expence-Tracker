import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import matplotlib.pyplot as plt
import numpy as np

# --- Style Constants ---

# Vibrant Color Palette
COLOR_BG = "#FAFAFA"              # Off-white background
COLOR_FRAME = "#FFFFFF"           # White for frames
COLOR_TEXT = "#212121"            # Dark grey for text
COLOR_PRIMARY = "#009688"         # Teal for primary actions
COLOR_SECONDARY = "#FF5722"       # Deep Orange for secondary actions
COLOR_EDIT = "#FFC107"            # Amber for edit
COLOR_DELETE = "#F44336"          # Red for delete
COLOR_SUCCESS = "#4CAF50"         # Green for success
COLOR_BUDGET_FRAME = "#E0F2F1"    # Light Teal for budget frame
COLOR_TREEVIEW_HEADER = "#B2DFDB" # Lighter Teal for Treeview header

# Font Styles
FONT_TITLE = ("Arial", 20, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 10, "bold")
FONT_ALERT = ("Arial", 12, "italic")
FONT_TREEVIEW_HEADER = ("Arial", 11, "bold")

# --- Global State ---
expenses = []
budget_limit = 0
categories = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]

# UI Widgets
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
        # Use tags for zebra striping
        tag = "oddrow" if len(expenses) % 2 == 0 else "evenrow"
        item_id = expense_list.insert("", "end", values=(category, f"₹{amount_float:.2f}"), tags=(tag,))
        expenses.append({'id': item_id, 'category': category, 'amount': amount_float})
        amount_entry.delete(0, tk.END)
        check_budget()
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a valid number for amount!")

def set_budget():
    global budget_limit
    try:
        budget_limit = float(budget_entry.get())
        budget_label.config(text=f"Budget Set: ₹{budget_limit:.2f}", fg=COLOR_SUCCESS)
        check_budget()
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a valid number for budget!")

def check_budget():
    total_spent = sum(expense['amount'] for expense in expenses)
    if budget_limit > 0 and total_spent > budget_limit:
        alert_label.config(text="⚠️ Budget Exceeded!", fg=COLOR_DELETE)
    else:
        if budget_limit > 0:
            alert_label.config(text="Budget is within limits", fg=COLOR_SUCCESS)
        else:
            alert_label.config(text="")

def plot_chart():
    if not expenses:
        messagebox.showinfo("No Data", "No expenses to display!")
        return

    category_totals = {cat: 0 for cat in categories}
    for expense in expenses:
        if expense['category'] in category_totals:
            category_totals[expense['category']] += expense['amount']

    filtered_totals = {k: v for k, v in category_totals.items() if v > 0}
    if not filtered_totals:
        messagebox.showinfo("No Data", "No expenses with positive amounts to display!")
        return

    labels = list(filtered_totals.keys())
    values = list(filtered_totals.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Expense Distribution")
    plt.axis('equal')
    plt.show()

def download_csv():
    file_path = "expenses.csv"
    try:
        full_path = os.path.abspath(file_path)
        rows_to_write = [(exp['category'], exp['amount']) for exp in expenses]
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Category", "Amount (₹)"])
            writer.writerows(rows_to_write)
        messagebox.showinfo("Download Complete", f"Expenses saved to:\n{full_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file: {e}")

def edit_expense():
    selected_item_id = expense_list.selection()
    if not selected_item_id:
        messagebox.showwarning("Selection Error", "Please select an expense to edit.")
        return

    item_id = selected_item_id[0]

    expense_to_edit = next((exp for exp in expenses if exp['id'] == item_id), None)

    if not expense_to_edit:
        messagebox.showerror("Error", "Could not find the selected expense to edit.")
        return

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Expense")
    edit_win.geometry("300x150")
    edit_win.configure(bg=COLOR_BG)

    tk.Label(edit_win, text="Category:", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=(10,0))
    edit_category_var = tk.StringVar(value=expense_to_edit['category'])
    edit_category_menu = ttk.Combobox(edit_win, textvariable=edit_category_var, values=categories, state="readonly")
    edit_category_menu.pack()

    tk.Label(edit_win, text="Amount (₹):", font=FONT_LABEL, bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=(10,0))
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
            expense_to_edit['category'] = new_category
            expense_to_edit['amount'] = new_amount

            expense_list.item(item_id, values=(new_category, f"₹{new_amount:.2f}"))

            check_budget()
            edit_win.destroy()
            messagebox.showinfo("Success", "Expense updated successfully.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid number for amount.", parent=edit_win)

    btn_frame = tk.Frame(edit_win, bg=COLOR_BG)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Save", command=save_changes, font=FONT_BUTTON, bg=COLOR_SUCCESS, fg="white").pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", command=edit_win.destroy, font=FONT_BUTTON, bg=COLOR_DELETE, fg="white").pack(side="left", padx=10)


def delete_expense():
    selected_item = expense_list.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an expense to delete.")
        return

    item_id = selected_item[0]

    confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this expense?")

    if confirm:
        expense_to_remove = next((exp for exp in expenses if exp['id'] == item_id), None)

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
    root.geometry("500x650")
    root.configure(bg=COLOR_BG)

    # --- Style Configuration ---
    style = ttk.Style()
    style.theme_use("clam") # Use a modern theme
    style.configure("Treeview.Heading",
        background=COLOR_TREEVIEW_HEADER,
        foreground=COLOR_TEXT,
        font=FONT_TREEVIEW_HEADER,
        relief="flat")
    style.map("Treeview.Heading",
        background=[('active', COLOR_PRIMARY)])
    style.configure("Treeview",
        background=COLOR_FRAME,
        fieldbackground=COLOR_FRAME,
        foreground=COLOR_TEXT,
        rowheight=25,
        font=FONT_LABEL)
    style.map("Treeview",
        background=[('selected', COLOR_PRIMARY)])

    # Zebra striping configuration
    expense_list.tag_configure('oddrow', background=COLOR_FRAME)
    expense_list.tag_configure('evenrow', background=COLOR_BG)


    # Main container frame for padding
    main_frame = tk.Frame(root, bg=COLOR_BG, padx=10, pady=10)
    main_frame.pack(fill="both", expand=True)

    title_label = tk.Label(main_frame, text="Expense Tracker", font=FONT_TITLE, fg=COLOR_TEXT, bg=COLOR_BG)
    title_label.pack(pady=(0, 20))

    # --- Budget Section ---
    budget_frame = tk.LabelFrame(main_frame, text="My Budget", font=FONT_LABEL, bg=COLOR_BUDGET_FRAME, fg=COLOR_TEXT, padx=10, pady=10)
    budget_frame.pack(fill="x", pady=(0, 10))

    tk.Label(budget_frame, text="Set Monthly Budget (₹):", font=FONT_LABEL, bg=COLOR_BUDGET_FRAME, fg=COLOR_TEXT).pack(side="left", padx=(0, 10))
    budget_entry = tk.Entry(budget_frame, width=15)
    budget_entry.pack(side="left", padx=(0, 10))
    tk.Button(budget_frame, text="Set", command=set_budget, font=FONT_BUTTON, bg=COLOR_PRIMARY, fg="white").pack(side="left")

    budget_label = tk.Label(main_frame, text="No Budget Set", font=FONT_ALERT, fg=COLOR_DELETE, bg=COLOR_BG)
    budget_label.pack(pady=(0, 10))

    # --- Add Expense Section ---
    expense_frame = tk.LabelFrame(main_frame, text="Add a New Expense", font=FONT_LABEL, bg=COLOR_FRAME, fg=COLOR_TEXT, padx=10, pady=10)
    expense_frame.pack(fill="x", pady=(0, 10))

    tk.Label(expense_frame, text="Category:", font=FONT_LABEL, bg=COLOR_FRAME, fg=COLOR_TEXT).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    category_var = tk.StringVar()
    category_menu = ttk.Combobox(expense_frame, textvariable=category_var, values=categories, state="readonly", width=25)
    category_menu.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(expense_frame, text="Amount (₹):", font=FONT_LABEL, bg=COLOR_FRAME, fg=COLOR_TEXT).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    amount_entry = tk.Entry(expense_frame, width=28)
    amount_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(expense_frame, text="Add Expense", command=add_expense, font=FONT_BUTTON, bg=COLOR_PRIMARY, fg="white").grid(row=2, column=0, columnspan=2, pady=10)

    # --- Expense List Section ---
    expense_list_frame = tk.Frame(main_frame)
    expense_list_frame.pack(fill="both", expand=True, pady=(0, 10))

    columns = ("Category", "Amount")
    expense_list = ttk.Treeview(expense_list_frame, columns=columns, show="headings")
    expense_list.heading("Category", text="Category")
    expense_list.heading("Amount", text="Amount")

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(expense_list_frame, orient="vertical", command=expense_list.yview)
    expense_list.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    expense_list.pack(side="left", fill="both", expand=True)

    # --- Action Buttons Section ---
    action_buttons_frame = tk.Frame(main_frame, bg=COLOR_BG)
    action_buttons_frame.pack(fill="x", pady=(0, 5))

    tk.Button(action_buttons_frame, text="Edit Selected", command=edit_expense, font=FONT_BUTTON, bg=COLOR_EDIT, fg=COLOR_TEXT).pack(side="left", expand=True, fill="x", padx=2)
    tk.Button(action_buttons_frame, text="Delete Selected", command=delete_expense, font=FONT_BUTTON, bg=COLOR_DELETE, fg="white").pack(side="left", expand=True, fill="x", padx=2)

    # --- Analysis & Download Section ---
    analysis_buttons_frame = tk.Frame(main_frame, bg=COLOR_BG)
    analysis_buttons_frame.pack(fill="x")

    tk.Button(analysis_buttons_frame, text="View Chart", command=plot_chart, font=FONT_BUTTON, bg=COLOR_SECONDARY, fg="white").pack(side="left", expand=True, fill="x", padx=2)
    tk.Button(analysis_buttons_frame, text="Download CSV", command=download_csv, font=FONT_BUTTON, bg=COLOR_SECONDARY, fg="white").pack(side="left", expand=True, fill="x", padx=2)

    # --- Alert Label ---
    alert_label = tk.Label(main_frame, text="", font=FONT_ALERT, bg=COLOR_BG)
    alert_label.pack(pady=(10, 0))

    root.mainloop()

if __name__ == "__main__":
    main()
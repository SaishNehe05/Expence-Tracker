import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import matplotlib.pyplot as plt
import numpy as np

# Global expense list
expenses = []
budget_limit = 0  # Default budget

# Categories for expenses
categories = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"]

# Function to add an expense
def add_expense():
    category = category_var.get()
    amount = amount_entry.get()
    
    if not category or not amount:
        messagebox.showwarning("Input Error", "Please fill in all fields!")
        return
    
    try:
        amount = float(amount)
        expenses.append((category, amount))
        expense_list.insert("", "end", values=(category, f"₹{amount:.2f}"))
        amount_entry.delete(0, tk.END)
        check_budget()
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a valid number for amount!")

# Function to set the budget
def set_budget():
    global budget_limit
    try:
        budget_limit = float(budget_entry.get())
        budget_label.config(text=f"Budget Set: ₹{budget_limit:.2f}", fg="green")
        check_budget()
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a valid number for budget!")

# Function to check if expenses exceed the budget
def check_budget():
    total_spent = sum(amount for _, amount in expenses)
    if budget_limit > 0 and total_spent > budget_limit:
        alert_label.config(text="⚠️ Budget Exceeded!", fg="red")
    else:
        alert_label.config(text="Budget is within limits", fg="blue")

# Function to visualize expenses
def plot_chart():
    if not expenses:
        messagebox.showinfo("No Data", "No expenses to display!")
        return

    category_totals = {cat: 0 for cat in categories}
    for cat, amt in expenses:
        category_totals[cat] += amt
    
    labels, values = zip(*[(k, v) for k, v in category_totals.items() if v > 0])
    values = np.array(values, dtype=np.float64)
    values = np.nan_to_num(values).astype(int)

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
    plt.title("Expense Distribution")
    plt.show()

# Function to download expenses as CSV
def download_csv():
    file_path = "C:/Users/saish/Documents/expenses.csv"  # Change path as needed

    with open(file_path, "w", newline="", encoding="utf-8") as file:  # Specify utf-8 encoding
        writer = csv.writer(file)
        writer.writerow(["Category", "Amount (₹)"])
        writer.writerows(expenses)
    messagebox.showinfo("Download Complete", f"Expenses saved as '{file_path}'.")


# Tkinter UI
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

# Alert Label
alert_label = tk.Label(root, text="", font=("Arial", 12, "bold"), bg="#F3F1F5")
alert_label.pack(pady=5)

# Buttons for analysis and CSV download
button_frame = tk.Frame(root, bg="#F3F1F5")
button_frame.pack(pady=10)
tk.Button(button_frame, text="View Chart", command=plot_chart, bg="#2196F3", fg="white").grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Download CSV", command=download_csv, bg="#9C27B0", fg="white").grid(row=0, column=1, padx=5)

# Run the Tkinter event loop
root.mainloop()

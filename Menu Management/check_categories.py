
# check_categories.py - Script to verify category assignments in tblMenuItem
# Used to ensure all menu items have correct category labels

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('menu.db')
cursor = conn.cursor()


# Query to fetch all menu items with their category
# Show all items with their categories
cursor.execute("SELECT Name, Category FROM tblMenuItem")
items = cursor.fetchall()

# Print each item with its category to verify correct assignment
# Categories should be: Fresh Fruit Juices, Sugarcane Juice, or Smoothies & Shakes
for item in items:
    print(f"Name: {item[0]}, Category: '{item[1]}'")

# Close database connection
conn.close()
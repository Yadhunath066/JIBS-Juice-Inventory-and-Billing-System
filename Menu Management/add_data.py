# add_data.py - Script to populate menu items into tblMenuItem database
# This script inserts 16 juice items from the Sip & Go PDF menu

import sqlite3

# Connect to the SQLite database

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# First, clear existing data
# Clear existing data to avoid duplicates when re-running the script
cursor.execute("DELETE FROM tblMenuItem")


# List of all menu items from the PDF
# Format: (Name, Price in øre, IsVegan, Category)
# Prices are stored as integers (e.g., 2900 = 29.00 DKK)



# All 16 items from PDF
items = [
    # Fresh Fruit Juices (6 items)
    ("Watermelon Juice", 2900, True, "Fresh Fruit Juices"),
    ("Mango Juice", 2900, True, "Fresh Fruit Juices"),
    ("Papaya Juice", 2900, True, "Fresh Fruit Juices"),
    ("Orange Juice", 2900, True, "Fresh Fruit Juices"),
    ("Pineapple Juice", 3200, True, "Fresh Fruit Juices"),
    ("Mixed Fruit Juice", 3500, True, "Fresh Fruit Juices"),
    
    # Sugarcane Juice (4 items)
    ("Classic Sugarcane", 2500, True, "Sugarcane Juice"),
    ("Ginger Sugarcane", 2900, True, "Sugarcane Juice"),
    ("Mint Sugarcane", 2900, True, "Sugarcane Juice"),
    ("Lemon Sugarcane", 2900, True, "Sugarcane Juice"),
    
    # Smoothies & Shakes (6 items)
    ("Mango Smoothie", 3900, True, "Smoothies & Shakes"),
    ("Tropical Blast", 4200, True, "Smoothies & Shakes"),
    ("Green Detox", 4200, True, "Smoothies & Shakes"),
    ("Strawberry Shake", 4200, True, "Smoothies & Shakes"),
    ("Banana Shake", 3900, True, "Smoothies & Shakes"),
    ("Berry Mix Smoothie", 4500, True, "Smoothies & Shakes"),
]


# Insert each item into the tblMenuItem table

for item in items:
    cursor.execute('''
        INSERT INTO tblMenuItem (Name, Price, IsVegan, Category)
        VALUES (?, ?, ?, ?)
    ''', item)


# Save changes and close connection

conn.commit()
conn.close()


# Confirm successful insertion

print(f"{len(items)} items added successfully!")
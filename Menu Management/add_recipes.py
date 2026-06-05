# add_recipes.py - Script to add sample recipe data linking menu items to stock ingredients
# This script creates relationships between menu items (tblMenuItem) and stock items (tblStock)


import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Sample recipes linking ItemID to StockID
# StockID 1 = Watermelon, StockID 2 = Mango, etc.
# Format: (ItemID, StockID, QuantityUsed)
# Note: Yadhunath will provide the actual StockIDs from his inventory system



recipes = [
    (1, 1, 200),   # Watermelon Juice needs 200g Watermelon
    (2, 2, 150),   # Mango Juice needs 150g Mango
    (3, 3, 200),   # Papaya Juice needs 200g Papaya
]

# Insert each recipe into the tblRecipe link table
# This table decomposes the many-to-many relationship between MenuItem and Stock

for recipe in recipes:
    cursor.execute('''
        INSERT INTO tblRecipe (ItemID, StockID, QuantityUsed)
        VALUES (?, ?, ?)
    ''', recipe)

# Save changes and close connection

conn.commit()
conn.close()
print("Sample recipes added!")
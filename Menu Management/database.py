# database.py - Script to create the tblRecipe table
# This table links menu items (tblMenuItem) to stock ingredients (tblStock)
# It decomposes the many-to-many relationship between MenuItem and Stock


import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Create tblRecipe table if it doesn't already exist
# RecipeID is the primary key
# ItemID references a menu item (foreign key to tblMenuItem)
# StockID references an ingredient (will connect to Yadhunath's tblStock)
# QuantityUsed stores how much of the ingredient is needed
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tblRecipe (
        RecipeID INTEGER PRIMARY KEY AUTOINCREMENT,
        ItemID INTEGER,
        StockID INTEGER,
        QuantityUsed INTEGER,
        FOREIGN KEY (ItemID) REFERENCES tblMenuItem(ItemID)
    )
''')

print("Recipe table created!")

# Save changes and close connection
conn.commit()
conn.close()
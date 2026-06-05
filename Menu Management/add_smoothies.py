# add_smoothies.py - Script to add smoothie items to tblMenuItem table
# This script adds the smoothie category items from the PDF menu


import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# List of smoothie items from the PDF menu
# Format: (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
# Prices are stored in øre (e.g., 3900 = 39.00 DKK)


smoothies = [
    ('Mango Smoothie', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Tropical Blast', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Green Detox', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Strawberry Shake', 4200, 5500, 6800, 'Smoothies & Shakes', 0, 1),
    ('Banana Shake', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Berry Mix Smoothie', 4500, 5800, 7200, 'Smoothies & Shakes', 1, 1)
]
# Insert each smoothie item into tblMenuItem
# IsActive = 1 means the item is active and visible in the menu

for item in smoothies:
    cursor.execute('''
        INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', item)

# Save changes
conn.commit()
print(f'Added {len(smoothies)} smoothies')

# Close database connection
conn.close()

# insert_data.py - Script to populate tblMenuItem with sample menu data
# This inserts all 16 juice items from the Sip & Go PDF menu

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Clear existing data to avoid duplicates when re-running
cursor.execute("DELETE FROM tblMenuItem")

# List of all menu items from the PDF menu
# Format: (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
# Prices are stored in øre (e.g., 2900 = 29.00 DKK)
# IsActive = 1 means item is active and visible
menu_items = [
    # Fresh Fruit Juices (6 items)
    ('Watermelon Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Mango Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Papaya Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Orange Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Pineapple Juice', 3200, 4200, 5200, 'Fresh Fruit Juices', 1, 1),
    ('Mixed Fruit Juice', 3500, 4500, 5500, 'Fresh Fruit Juices', 1, 1),

     # Sugarcane Juice (4 items)
    ('Classic Sugarcane', 2500, 3500, 4500, 'Sugarcane Juice', 1, 1),
    ('Ginger Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1, 1),
    ('Mint Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1, 1),
    ('Lemon Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1, 1),

    # Smoothies & Shakes (6 items)
    ('Mango Smoothie', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Tropical Blast', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Green Detox', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Strawberry Shake', 4200, 5500, 6800, 'Smoothies & Shakes', 0, 1),
    ('Banana Shake', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Berry Mix Smoothie', 4500, 5800, 7200, 'Smoothies & Shakes', 1, 1)
]

# Insert all items into tblMenuItem using executemany for efficiency
cursor.executemany('''
    INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', menu_items)


# Save changes
conn.commit()
conn.close()

print("Sample data inserted successfully!")
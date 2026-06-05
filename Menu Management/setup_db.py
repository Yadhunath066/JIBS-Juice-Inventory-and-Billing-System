# setup_db.py - Script to create tblMenuItem table and populate with sample menu data
# Run this script once to set up the database for the Menu Management system


import sqlite3


# Connect to the SQLite database (creates menu.db if it doesn't exist)
conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Create tblMenuItem table
# This table stores all menu items with their prices and properties
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tblMenuItem (
        ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE,
        PriceSm INTEGER NOT NULL,
        PriceReg INTEGER NOT NULL,
        PriceLg INTEGER NOT NULL,
        Category TEXT NOT NULL,
        IsVegan INTEGER DEFAULT 0,
        IsActive INTEGER DEFAULT 1
    )
''')

# Insert sample data if table is empty
cursor.execute("SELECT COUNT(*) FROM tblMenuItem")
count = cursor.fetchone()[0]

# Only insert sample data if table is empty (avoid duplicates)
if count == 0:
    sample_items = [
        # Fresh Fruit Juices (6 items)
        ('Watermelon Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Mango Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Papaya Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Orange Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Pineapple Juice', 3200, 4200, 5200, 'Fresh Fruit Juices', 1),

        # Sugarcane Juice (4 items)
        ('Classic Sugarcane', 2500, 3500, 4500, 'Sugarcane Juice', 1),
        ('Ginger Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1),
        ('Mint Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1),
        ('Lemon Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1),

        # Smoothies & Shakes (6 items)
        ('Mango Smoothie', 3900, 5200, 6500, 'Smoothies & Shakes', 1),
        ('Tropical Blast', 4200, 5500, 6800, 'Smoothies & Shakes', 1),
        ('Green Detox', 4200, 5500, 6800, 'Smoothies & Shakes', 1),
        ('Strawberry Shake', 4200, 5500, 6800, 'Smoothies & Shakes', 1),
        ('Banana Shake', 3900, 5200, 6500, 'Smoothies & Shakes', 1),
        ('Berry Mix Smoothie', 4500, 5800, 7200, 'Smoothies & Shakes', 1),
    ]
    # Insert each sample item into the table
    # IsActive is set to 1 (active) for all sample items

    for item in sample_items:
        cursor.execute('''
            INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', item)
    
    conn.commit()
    print(f"Added {len(sample_items)} sample items to tblMenuItem")

# Save changes and close connection
conn.commit()
conn.close()

print("Database setup complete!")
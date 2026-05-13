import sqlite3

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Create tblMenuItem table
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

if count == 0:
    sample_items = [
        ('Watermelon Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Mango Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Papaya Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Orange Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1),
        ('Pineapple Juice', 3200, 4200, 5200, 'Fresh Fruit Juices', 1),
        ('Classic Sugarcane', 2500, 3500, 4500, 'Sugarcane Juice', 1),
        ('Ginger Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1),
        ('Mint Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1),
        ('Lemon Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1),
        ('Mango Smoothie', 3900, 5200, 6500, 'Smoothies & Shakes', 1),
        ('Tropical Blast', 4200, 5500, 6800, 'Smoothies & Shakes', 1),
        ('Green Detox', 4200, 5500, 6800, 'Smoothies & Shakes', 1),
        ('Strawberry Shake', 4200, 5500, 6800, 'Smoothies & Shakes', 1),
        ('Banana Shake', 3900, 5200, 6500, 'Smoothies & Shakes', 1),
        ('Berry Mix Smoothie', 4500, 5800, 7200, 'Smoothies & Shakes', 1),
    ]
    
    for item in sample_items:
        cursor.execute('''
            INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', item)
    
    conn.commit()
    print(f"Added {len(sample_items)} sample items to tblMenuItem")

conn.commit()
conn.close()

print("Database setup complete!")
import sqlite3

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Clear existing data
cursor.execute("DELETE FROM tblMenuItem")

# Insert sample menu items
menu_items = [
    ('Watermelon Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Mango Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Papaya Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Orange Juice', 2900, 3900, 4900, 'Fresh Fruit Juices', 1, 1),
    ('Pineapple Juice', 3200, 4200, 5200, 'Fresh Fruit Juices', 1, 1),
    ('Mixed Fruit Juice', 3500, 4500, 5500, 'Fresh Fruit Juices', 1, 1),
    ('Classic Sugarcane', 2500, 3500, 4500, 'Sugarcane Juice', 1, 1),
    ('Ginger Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1, 1),
    ('Mint Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1, 1),
    ('Lemon Sugarcane', 2900, 3900, 4900, 'Sugarcane Juice', 1, 1),
    ('Mango Smoothie', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Tropical Blast', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Green Detox', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Strawberry Shake', 4200, 5500, 6800, 'Smoothies & Shakes', 0, 1),
    ('Banana Shake', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Berry Mix Smoothie', 4500, 5800, 7200, 'Smoothies & Shakes', 1, 1)
]

cursor.executemany('''
    INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', menu_items)

conn.commit()
conn.close()

print("Sample data inserted successfully!")
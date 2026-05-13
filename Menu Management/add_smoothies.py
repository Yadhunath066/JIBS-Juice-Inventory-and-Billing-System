import sqlite3

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

smoothies = [
    ('Mango Smoothie', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Tropical Blast', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Green Detox', 4200, 5500, 6800, 'Smoothies & Shakes', 1, 1),
    ('Strawberry Shake', 4200, 5500, 6800, 'Smoothies & Shakes', 0, 1),
    ('Banana Shake', 3900, 5200, 6500, 'Smoothies & Shakes', 0, 1),
    ('Berry Mix Smoothie', 4500, 5800, 7200, 'Smoothies & Shakes', 1, 1)
]

for item in smoothies:
    cursor.execute('''
        INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', item)

conn.commit()
print(f'Added {len(smoothies)} smoothies')
conn.close()
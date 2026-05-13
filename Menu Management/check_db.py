import sqlite3

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Count smoothies
cursor.execute('SELECT COUNT(*) FROM tblMenuItem WHERE Category = "Smoothies & Shakes"')
count = cursor.fetchone()[0]
print(f'Number of smoothies: {count}')

# Show all smoothies
cursor.execute('SELECT Name, PriceSm, PriceReg, PriceLg FROM tblMenuItem WHERE Category = "Smoothies & Shakes"')
smoothies = cursor.fetchall()
for s in smoothies:
    print(s)

conn.close()
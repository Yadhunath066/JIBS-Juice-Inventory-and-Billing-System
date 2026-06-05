
# check_db.py - Script to verify smoothie items in the database
# Used to check if smoothies are correctly inserted into tblMenuItem

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('menu.db')
cursor = conn.cursor()


# Count the number of smoothie items in the database
cursor.execute('SELECT COUNT(*) FROM tblMenuItem WHERE Category = "Smoothies & Shakes"')
count = cursor.fetchone()[0]
print(f'Number of smoothies: {count}')

# Display all smoothie items with their prices for Sm, Reg, Lg sizes
cursor.execute('SELECT Name, PriceSm, PriceReg, PriceLg FROM tblMenuItem WHERE Category = "Smoothies & Shakes"')
smoothies = cursor.fetchall()
for s in smoothies:
    print(s)

# Close database connection
conn.close()
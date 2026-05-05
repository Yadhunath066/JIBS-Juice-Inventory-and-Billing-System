import sqlite3

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Sample recipes (linking ItemID to StockID)
# StockID 1 = Watermelon, StockID 2 = Mango, etc. (Yadhunath will provide actual StockIDs)
recipes = [
    (1, 1, 200),   # Watermelon Juice needs 200g Watermelon
    (2, 2, 150),   # Mango Juice needs 150g Mango
    (3, 3, 200),   # Papaya Juice needs 200g Papaya
]

for recipe in recipes:
    cursor.execute('''
        INSERT INTO tblRecipe (ItemID, StockID, QuantityUsed)
        VALUES (?, ?, ?)
    ''', recipe)

conn.commit()
conn.close()
print("Sample recipes added!")
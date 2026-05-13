import sqlite3

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Create recipe table
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

conn.commit()
conn.close()
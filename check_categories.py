import sqlite3

conn = sqlite3.connect('menu.db')
cursor = conn.cursor()

# Show all items with their categories
cursor.execute("SELECT Name, Category FROM tblMenuItem")
items = cursor.fetchall()

for item in items:
    print(f"Name: {item[0]}, Category: '{item[1]}'")

conn.close()
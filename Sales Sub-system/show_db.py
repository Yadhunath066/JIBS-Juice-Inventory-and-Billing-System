import sqlite3

conn = sqlite3.connect('jibs.db')
cursor = conn.cursor()

# Show all tables
print("=== ALL TABLES IN DATABASE ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# Show tblSale structure
print("\n=== tblSale TABLE STRUCTURE ===")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tblSale'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("Table 'tblSale' not found")

# Show tblSale data
print("\n=== tblSale DATA ===")
cursor.execute("SELECT * FROM tblSale")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(row)
else:
    print("No data in tblSale")

# Check if tblSaleLine exists
print("\n=== tblSaleLine ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tblSaleLine'")
if cursor.fetchone():
    print("tblSaleLine table exists")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tblSaleLine'")
    print(cursor.fetchone()[0])
else:
    print("tblSaleLine table does NOT exist yet")

conn.close()
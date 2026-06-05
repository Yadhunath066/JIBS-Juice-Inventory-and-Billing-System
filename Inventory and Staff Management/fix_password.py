import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="jibs_inventory and staff"
)

cursor = conn.cursor()
hashed_password = generate_password_hash('admin123')
cursor.execute("UPDATE tblstaff SET PasswordHash = %s WHERE Username = %s", (hashed_password, 'yadhunath'))
conn.commit()
print("Password updated successfully!")
conn.close()

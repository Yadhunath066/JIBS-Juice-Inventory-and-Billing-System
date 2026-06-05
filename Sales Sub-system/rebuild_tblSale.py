# rebuild_tblSale.py
# Recreates tblSale with correct constraints:
# - PaymentMethod TEXT NOT NULL
# - IsProcessed INTEGER DEFAULT 1
# - StaffID INTEGER REFERENCES tblStaff(StaffID)
# Preserves all existing order data and foreign keys from tblSaleLine.
# For JIBS Sales Sub-system - Sanjaya Thakuri

import sqlite3

def rebuild_table():
    conn = sqlite3.connect('jibs.db')
    cursor = conn.cursor()
    
    # Begin transaction
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        # Step 1: Backup existing data from tblSale
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tblSale'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("Backing up existing tblSale data...")
            cursor.execute("SELECT * FROM tblSale")
            rows = cursor.fetchall()
            cursor.execute("PRAGMA table_info(tblSale)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Found {len(rows)} rows with columns: {columns}")
        else:
            rows = []
            print("No existing tblSale table found. Creating fresh.")
        
        # Step 2: Check if tblSaleLine exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tblSaleLine'")
        has_saleline = cursor.fetchone() is not None
        
        # Step 3: Drop old tblSale (disable foreign keys temporarily)
        if has_saleline:
            cursor.execute("PRAGMA foreign_keys = OFF")
        
        if table_exists:
            cursor.execute("DROP TABLE tblSale")
            print("Dropped old tblSale table.")
        
        # Step 4: Create new table with correct schema including FOREIGN KEY on StaffID
        cursor.execute('''
            CREATE TABLE tblSale (
                SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
                SaleDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                TotalAmount INTEGER NOT NULL,
                PaymentMethod TEXT NOT NULL,
                StaffID INTEGER,
                ItemCount INTEGER NOT NULL,
                IsProcessed INTEGER DEFAULT 1,
                FOREIGN KEY (StaffID) REFERENCES tblStaff(StaffID)
            )
        ''')
        print("Created new tblSale with PaymentMethod NOT NULL, IsProcessed INTEGER, and FOREIGN KEY (StaffID).")
        
        # Step 5: Restore data if we had any
        if rows:
            print("Restoring data...")
            for row in rows:
                row_len = len(row)
                if row_len == 7:
                    sale_id, sale_date, total, payment, staff, item_count, is_processed = row
                elif row_len == 6:
                    sale_id, sale_date, total, payment, staff, item_count = row
                    is_processed = 1
                else:
                    sale_id, sale_date, total, payment, staff, item_count = row[:6]
                    is_processed = 1
                
                if payment is None:
                    payment = 'Unknown'
                
                # The foreign key expects StaffID to exist in tblStaff.
                # Your existing data has StaffID=1 for all rows. We assume tblStaff has a row with StaffID=1.
                # If not, you may need to insert it first.
                cursor.execute('''
                    INSERT INTO tblSale 
                    (SaleID, SaleDate, TotalAmount, PaymentMethod, StaffID, ItemCount, IsProcessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (sale_id, sale_date, total, payment, staff, item_count, is_processed))
            
            print(f"Restored {len(rows)} rows.")
        
        # Step 6: Re-enable foreign key checks
        if has_saleline:
            cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit transaction
        conn.commit()
        print("SUCCESS: Table rebuilt with foreign key. Data restored.")
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        print("Transaction rolled back. No changes made.")
    
    finally:
        conn.close()

if __name__ == "__main__":
    rebuild_table()
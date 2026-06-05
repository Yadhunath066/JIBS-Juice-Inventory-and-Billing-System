"""
Test Staff Delete - GDPR Anonymisation
"""

import mysql.connector
from werkzeug.security import generate_password_hash
import uuid

def run_test():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="jibs_inventory and staff"
    )
    cursor = conn.cursor()
    
    print("=" * 70)
    print("TEST: Staff Delete - GDPR Anonymisation")
    print("=" * 70)
    
    # Create unique test staff to avoid conflicts
    unique_id = uuid.uuid4().hex[:8]
    test_username = f"test_gdpr_user_{unique_id}"
    deleted_username = f"deleted_user_{unique_id}"
    
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_gdpr_user_%'")
    cursor.execute("""
        INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
        VALUES (%s, %s, %s, %s, %s)
    """, ("GDPR Test User", test_username, generate_password_hash('pass123'), 'Cashier', 1))
    conn.commit()
    
    cursor.execute("SELECT StaffID FROM tblStaff WHERE Username = %s", (test_username,))
    staff_id = cursor.fetchone()[0]
    
    # GDPR Delete (anonymise) - use unique deleted username
    cursor.execute("""
        UPDATE tblStaff 
        SET FullName='[ANONYMIZED]', Username=%s, IsActive=0
        WHERE StaffID = %s
    """, (deleted_username, staff_id))
    conn.commit()
    
    # Verify
    cursor.execute("SELECT FullName, Username, IsActive FROM tblStaff WHERE StaffID = %s", (staff_id,))
    result = cursor.fetchone()
    
    if result[0] == '[ANONYMIZED]' and result[1] == deleted_username and result[2] == 0:
        print("✅ PASS: GDPR anonymisation successful")
        passed = 1
    else:
        print(f"❌ FAIL: GDPR anonymisation failed - got FullName={result[0]}, Username={result[1]}, IsActive={result[2]}")
        passed = 0
    
    # Clean up
    cursor.execute("DELETE FROM tblStaff WHERE StaffID = %s", (staff_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {0 if passed else 1}")
    return passed, 0 if passed else 1

if __name__ == "__main__":
    run_test()
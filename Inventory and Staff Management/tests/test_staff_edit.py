"""
Test Staff Edit - Update Validation
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
    print("TEST: Staff Edit - Update Validation")
    print("=" * 70)
    
    # Create unique test staff to avoid conflicts
    unique_id = uuid.uuid4().hex[:8]
    test_username = f"test_edit_user_{unique_id}"
    original_name = f"Original Name {unique_id}"
    
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_edit_user_%'")
    cursor.execute("""
        INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
        VALUES (%s, %s, %s, %s, %s)
    """, (original_name, test_username, generate_password_hash('pass123'), 'Cashier', 1))
    conn.commit()
    
    cursor.execute("SELECT StaffID FROM tblStaff WHERE Username = %s", (test_username,))
    staff_id = cursor.fetchone()[0]
    
    test_cases = [
        ("Update name", f"New Name {unique_id}", "Cashier", 1),  # Keep as Cashier
        ("Update role to Admin", f"New Name {unique_id}", "Admin", 1),  # Change role
        ("Deactivate staff", f"New Name {unique_id}", "Admin", 0),  # Set inactive
    ]
    
    passed = 0
    failed = 0
    
    for test_name, new_name, new_role, is_active in test_cases:
        try:
            cursor.execute("""
                UPDATE tblStaff SET FullName = %s, Role = %s, IsActive = %s
                WHERE StaffID = %s
            """, (new_name, new_role, is_active, staff_id))
            conn.commit()
            
            cursor.execute("SELECT FullName, Role, IsActive FROM tblStaff WHERE StaffID = %s", (staff_id,))
            result = cursor.fetchone()
            
            if result[0] == new_name and result[1] == new_role and result[2] == is_active:
                print(f"✅ PASS: {test_name} - Name={result[0]}, Role={result[1]}, Active={result[2]}")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - Expected Name={new_name}, Role={new_role}, Active={is_active}, Got Name={result[0]}, Role={result[1]}, Active={result[2]}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
            failed += 1
            conn.rollback()
    
    # Clean up
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_edit_user_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
"""
Test Filter Staff by Role
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
    print("TEST: Filter Staff by Role")
    print("=" * 70)
    
    # Create unique test staff with different roles
    unique_id = uuid.uuid4().hex[:6]
    
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_filter_%'")
    
    test_staff = [
        (f"Admin User {unique_id}", f"admin_filter_{unique_id}", "Admin"),
        (f"Cashier One {unique_id}", f"cashier1_filter_{unique_id}", "Cashier"),
        (f"Cashier Two {unique_id}", f"cashier2_filter_{unique_id}", "Cashier"),
    ]
    
    for name, username, role in test_staff:
        cursor.execute("""
            INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, f"test_filter_{username}", generate_password_hash('pass123'), role, 1))
    conn.commit()
    
    test_cases = [
        ("Filter Admin", "Admin", 1),
        ("Filter Cashier", "Cashier", 2),
        ("Filter Invalid", "Manager", 0),
        ("No filter", "all", 3),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, role, expected_count in test_cases:
        if role == "all":
            cursor.execute("SELECT * FROM tblStaff WHERE Username LIKE 'test_filter_%'")
        else:
            cursor.execute("SELECT * FROM tblStaff WHERE Role = %s AND Username LIKE 'test_filter_%'", (role,))
        results = cursor.fetchall()
        actual_count = len(results)
        
        if actual_count == expected_count:
            print(f"✅ PASS: {test_name} - found {actual_count} results")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name} - expected {expected_count}, got {actual_count}")
            failed += 1
    
    # Clean up
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_filter_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
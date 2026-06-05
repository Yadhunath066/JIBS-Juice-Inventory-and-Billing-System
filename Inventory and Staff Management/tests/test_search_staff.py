"""
Test Search Staff by Name
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
    print("TEST: Search Staff by Name")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    
    # Create test staff with unique names
    test_staff = [
        (f"John Smith {unique_id}", f"john_{unique_id}"),
        (f"Jane Doe {unique_id}", f"jane_{unique_id}"),
        (f"Bob Johnson {unique_id}", f"bob_{unique_id}"),
    ]
    
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_search_%'")
    for name, username in test_staff:
        cursor.execute("""
            INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, f"test_search_{username}", generate_password_hash('pass123'), 'Cashier', 1))
    conn.commit()
    
    test_cases = [
        ("Search by full name", test_staff[0][0], 1),
        ("Search by partial name", "John", 1),
        ("Search by first letter", "J", 1),
        ("Search non-existent", "XYZ", 0),
        ("Empty search", "", 3),
        ("Case insensitive", "john", 1),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, search_term, expected_count in test_cases:
        if search_term:
            cursor.execute("SELECT * FROM tblStaff WHERE FullName LIKE %s AND Username LIKE 'test_search_%'", (f'%{search_term}%',))
        else:
            cursor.execute("SELECT * FROM tblStaff WHERE Username LIKE 'test_search_%'")
        results = cursor.fetchall()
        actual_count = len(results)
        
        if actual_count == expected_count:
            print(f"✅ PASS: {test_name} - found {actual_count} results")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name} - expected {expected_count}, got {actual_count}")
            failed += 1
    
    # Clean up
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_search_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
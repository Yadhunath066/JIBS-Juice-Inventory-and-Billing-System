"""
Test Login - Username and Password Validation
"""

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
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
    print("TEST: Login Validation")
    print("=" * 70)
    
    # Create unique test user for this run
    unique_id = uuid.uuid4().hex[:8]
    test_username = f"testlogin_{unique_id}"
    test_password = f"Test@{unique_id[:6]}123"
    
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'testlogin_%'")
    cursor.execute("""
        INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
        VALUES (%s, %s, %s, %s, %s)
    """, ("Test User", test_username, generate_password_hash(test_password), "Cashier", 1))
    conn.commit()
    
    test_cases = [
        ("Valid credentials", test_username, test_password, True),
        ("Wrong password", test_username, "wrongpass", False),
        ("Wrong username", "wronguser", test_password, False),
        ("Empty username", "", test_password, False),
        ("Empty password", test_username, "", False),
        ("Both empty", "", "", False),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, username, password, expected in test_cases:
        try:
            if username and username.startswith('testlogin_'):
                # Use exact username for valid test
                cursor.execute("SELECT * FROM tblStaff WHERE Username = %s AND IsActive = 1", (username,))
            elif username == "":
                # Empty username - no need to query
                staff = None
            else:
                cursor.execute("SELECT * FROM tblStaff WHERE Username = %s AND IsActive = 1", (username,))
            
            if username != "":
                staff = cursor.fetchone()
            else:
                staff = None
            
            if staff and check_password_hash(staff[3], password):
                actual = True
            else:
                actual = False
            
            if actual == expected:
                print(f"✅ PASS: {test_name}")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} (expected {expected}, got {actual})")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
            failed += 1
    
    # Clean up
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'testlogin_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
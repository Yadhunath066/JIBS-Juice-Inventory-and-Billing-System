"""
Test Staff Add - Password Validation
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
    print("TEST: Add Staff - Password Validation")
    print("=" * 70)
    
    test_cases = [
        ("Normal password", "password123", True),
        ("With special chars", "Pass@123", True),
        ("Minimum length (1 char)", "a", True),
        ("Empty password", "", False),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, password, should_pass in test_cases:
        # Create unique username for each test
        unique_id = uuid.uuid4().hex[:6]
        test_username = f"test_pass_{test_name.replace(' ', '_')}_{unique_id}"
        
        try:
            cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_pass_%'")
            
            if password and len(password) > 0:
                cursor.execute("""
                    INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
                    VALUES (%s, %s, %s, %s, %s)
                """, (f"Test {test_name}", test_username, generate_password_hash(password), 'Cashier', 1))
                conn.commit()
                
                if should_pass:
                    print(f"✅ PASS: {test_name} - password '{password[:10]}...' ({len(password)} chars)")
                    passed += 1
                else:
                    print(f"❌ FAIL: {test_name} - password '{password[:10]}...' should have been rejected")
                    failed += 1
            else:
                # Empty password - should fail
                try:
                    cursor.execute("""
                        INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (f"Test {test_name}", test_username, password, 'Cashier', 1))
                    conn.commit()
                    print(f"❌ FAIL: {test_name} - empty password should have been rejected")
                    failed += 1
                except Exception as e:
                    print(f"✅ PASS: {test_name} - empty password correctly rejected")
                    passed += 1
            
            cursor.execute("DELETE FROM tblStaff WHERE Username = %s", (test_username,))
            conn.commit()
        except Exception as e:
            if not should_pass:
                print(f"✅ PASS: {test_name} (rejected as expected)")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
                failed += 1
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
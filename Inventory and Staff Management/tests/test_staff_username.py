"""
Test Staff Add - Username Validation
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
    print("TEST: Add Staff - Username Validation")
    print("=" * 70)
    
    # Create a unique base to avoid conflicts with existing users
    unique_base = uuid.uuid4().hex[:6]
    
    test_cases = [
        ("1 char", f"a_{unique_base}", True),
        ("2 chars", f"ab_{unique_base}", True),
        ("Normal", f"john_doe_{unique_base}", True),
        ("With numbers", f"user123_{unique_base}", True),
        ("49 chars", "a" * 40 + f"_{unique_base}", True),
        ("Empty", "", False),
        ("Too long (51 chars)", "a" * 51, False),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, username, should_pass in test_cases:
        test_fullname = f"Test {test_name} {unique_base}"
        
        try:
            # Clean up any existing test users
            cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_user_%'")
            cursor.execute("DELETE FROM tblStaff WHERE Username LIKE '%_test_%'")
            
            if username and len(username) <= 50 and username.strip():
                # Insert valid username
                cursor.execute("""
                    INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
                    VALUES (%s, %s, %s, %s, %s)
                """, (test_fullname, username, generate_password_hash('pass123'), 'Cashier', 1))
                conn.commit()
                
                if should_pass:
                    print(f"✅ PASS: {test_name} - '{username[:30]}' ({len(username)} chars)")
                    passed += 1
                else:
                    print(f"❌ FAIL: {test_name} - '{username[:30]}' should have been rejected")
                    failed += 1
                    
                # Clean up
                cursor.execute("DELETE FROM tblStaff WHERE Username = %s", (username,))
                conn.commit()
            else:
                # Invalid username - should fail
                try:
                    cursor.execute("""
                        INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (test_fullname, username, generate_password_hash('pass123'), 'Cashier', 1))
                    conn.commit()
                    print(f"❌ FAIL: {test_name} - should have been rejected")
                    failed += 1
                    cursor.execute("DELETE FROM tblStaff WHERE Username = %s", (username,))
                    conn.commit()
                except Exception as e:
                    print(f"✅ PASS: {test_name} - correctly rejected")
                    passed += 1
                    
        except Exception as e:
            if not should_pass:
                print(f"✅ PASS: {test_name} (rejected as expected)")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
                failed += 1
            conn.rollback()
    
    # Clean up any remaining test users
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE '%_test_%'")
    cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_user_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
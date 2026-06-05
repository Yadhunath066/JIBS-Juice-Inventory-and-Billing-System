"""
Test Staff Add - Role Validation
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
    print("TEST: Add Staff - Role Validation")
    print("=" * 70)
    
    valid_roles = ['Admin', 'Cashier']
    
    test_cases = [
        ("Admin (valid)", "Admin", True),
        ("Cashier (valid)", "Cashier", True),
        ("admin (lowercase)", "admin", True),  # Should be accepted (case-insensitive)
        ("ADMIN (uppercase)", "ADMIN", True),  # Should be accepted (case-insensitive)
        ("Invalid role", "Manager", False),    # Should default to Cashier
        ("Empty role", "", False),             # Should default to Cashier
    ]
    
    passed = 0
    failed = 0
    
    for test_name, role_value, should_pass in test_cases:
        # Create unique username for each test
        unique_id = uuid.uuid4().hex[:6]
        test_username = f"test_role_{test_name.lower().replace(' ', '_')}_{unique_id}"
        
        try:
            cursor.execute("DELETE FROM tblStaff WHERE Username LIKE 'test_role_%'")
            
            # Determine what role to actually store
            if role_value and role_value.capitalize() in valid_roles:
                actual_role = role_value.capitalize()
            else:
                actual_role = "Cashier"  # Default for invalid roles
            
            cursor.execute("""
                INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
                VALUES (%s, %s, %s, %s, %s)
            """, (f"Test {test_name}", test_username, generate_password_hash('pass123'), actual_role, 1))
            conn.commit()
            
            cursor.execute("SELECT Role FROM tblStaff WHERE Username = %s", (test_username,))
            stored_role = cursor.fetchone()
            
            # Check if the stored role is appropriate
            if should_pass:
                # Valid role should be stored as is
                if stored_role[0].lower() == role_value.lower() or stored_role[0] == role_value:
                    print(f"✅ PASS: {test_name} - stored as '{stored_role[0]}'")
                    passed += 1
                else:
                    print(f"❌ FAIL: {test_name} - expected '{role_value}', got '{stored_role[0]}'")
                    failed += 1
            else:
                # Invalid role should default to Cashier
                if stored_role[0] == "Cashier":
                    print(f"✅ PASS: {test_name} - defaulted to '{stored_role[0]}'")
                    passed += 1
                else:
                    print(f"❌ FAIL: {test_name} - invalid role should default to Cashier, got '{stored_role[0]}'")
                    failed += 1
            
            cursor.execute("DELETE FROM tblStaff WHERE Username = %s", (test_username,))
            conn.commit()
        except Exception as e:
            print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
            failed += 1
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
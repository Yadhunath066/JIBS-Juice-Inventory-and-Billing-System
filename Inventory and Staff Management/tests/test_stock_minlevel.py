"""
Test Stock Add - Minimum Stock Level Validation
"""

import mysql.connector
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
    print("TEST: Add Stock - Minimum Stock Level Validation")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    
    test_cases = [
        ("Zero (boundary)", 0, True),
        ("Positive number", 10, True),
        ("Large number", 5000, True),
        ("Negative number", -1, False),
        ("Invalid - letters", "xyz", False),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, min_level, should_pass in test_cases:
        # Create unique ingredient name for each test
        test_ingredient = f"TEST_MIN_{test_name.replace(' ', '_')}_{unique_id}"
        
        try:
            cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_MIN_%'")
            
            if isinstance(min_level, int) and min_level >= 0:
                cursor.execute("""
                    INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (test_ingredient, 100, min_level, 'kg', 0, 'Fruits'))
                conn.commit()
                
                if should_pass:
                    print(f"✅ PASS: {test_name} - {min_level}")
                    passed += 1
                else:
                    print(f"❌ FAIL: {test_name} - {min_level} (should have been rejected)")
                    failed += 1
            else:
                # Invalid data type - should fail
                try:
                    cursor.execute("""
                        INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (test_ingredient, 100, min_level, 'kg', 0, 'Fruits'))
                    conn.commit()
                    print(f"❌ FAIL: {test_name} - {min_level} (should have been rejected)")
                    failed += 1
                except:
                    print(f"✅ PASS: {test_name} - {min_level} (correctly rejected)")
                    passed += 1
            
            # Clean up
            cursor.execute("DELETE FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
            conn.commit()
        except Exception as e:
            if not should_pass:
                print(f"✅ PASS: {test_name} - {min_level} (rejected)")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - {min_level} - {str(e)[:50]}")
                failed += 1
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
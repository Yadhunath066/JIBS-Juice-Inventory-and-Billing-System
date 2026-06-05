"""
Test Stock Add - Quantity Field Validation
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
    print("TEST: Add Stock - Quantity Field Validation")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    
    test_cases = [
        ("Zero (boundary)", 0, True),
        ("Positive number", 50, True),
        ("Large number", 5000, True),
        ("Negative number", -1, False),
        ("Invalid - letters", "abc", False),
        ("Invalid - decimal", 10.5, False),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, quantity, should_pass in test_cases:
        # Create unique ingredient name for each test
        test_ingredient = f"TEST_QTY_{test_name.replace(' ', '_')}_{unique_id}"
        
        try:
            cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_QTY_%'")
            
            if isinstance(quantity, int) and quantity >= 0:
                cursor.execute("""
                    INSERT INTO tblStock (IngredientName, Category, QuantityInStock, MinStockLevel, UnitType, IsPerishable)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (test_ingredient, "Fruits", quantity, 10, 'kg', 0))
                conn.commit()
                
                if should_pass:
                    print(f"✅ PASS: {test_name} - {quantity}")
                    passed += 1
                else:
                    print(f"❌ FAIL: {test_name} - {quantity} (should have been rejected)")
                    failed += 1
            else:
                # Invalid data type - should fail
                try:
                    cursor.execute("""
                        INSERT INTO tblStock (IngredientName, Category, QuantityInStock, MinStockLevel, UnitType, IsPerishable)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (test_ingredient, "Fruits", quantity, 10, 'kg', 0))
                    conn.commit()
                    print(f"❌ FAIL: {test_name} - {quantity} (should have been rejected)")
                    failed += 1
                except Exception as e:
                    print(f"✅ PASS: {test_name} - {quantity} (correctly rejected: {str(e)[:30]})")
                    passed += 1
            
            # Clean up
            cursor.execute("DELETE FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
            conn.commit()
        except Exception as e:
            if not should_pass:
                print(f"✅ PASS: {test_name} - {quantity} (rejected as expected)")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - {quantity} - {str(e)[:50]}")
                failed += 1
            conn.rollback()
    
    # Clean up any remaining test ingredients
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_QTY_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
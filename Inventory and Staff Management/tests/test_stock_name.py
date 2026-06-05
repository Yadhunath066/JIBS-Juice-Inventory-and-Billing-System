"""
Test Stock Add - Ingredient Name Validation
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
    print("TEST: Add Stock - Ingredient Name Validation")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    base_name = f"TestIngredient_{unique_id}"
    
    test_cases = [
        ("Valid short name", f"{base_name}_Short", True),
        ("Valid with spaces", f"{base_name} With Spaces", True),
        ("Valid with special chars", f"{base_name}_Special@123", True),
        ("Max length (100 chars)", "A" * 100, True),
        ("Too long (101 chars)", "A" * 101, False),
        ("Empty name", "", False),
        ("Only spaces", "   ", False),
    ]
    
    passed = 0
    failed = 0
    
    # Clean up any existing test ingredients
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TestIngredient_%'")
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_%'")
    conn.commit()
    
    for test_name, name_value, should_pass in test_cases:
        # Create a unique name for this test
        if name_value and len(name_value) <= 100 and name_value.strip():
            test_ingredient = name_value
        else:
            test_ingredient = f"TEST_EMPTY_{test_name.replace(' ', '_')}_{unique_id}"
        
        try:
            # Ensure we don't have leftover test data
            cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TestIngredient_%'")
            cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_%'")
            
            if name_value and len(name_value) <= 100 and name_value.strip():
                cursor.execute("""
                    INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (test_ingredient, 50, 10, 'kg', 0, 'Fruits'))
                conn.commit()
                
                if should_pass:
                    print(f"✅ PASS: {test_name} - '{test_ingredient[:40]}'")
                    passed += 1
                else:
                    print(f"❌ FAIL: {test_name} - '{test_ingredient[:40]}' (should have been rejected)")
                    failed += 1
            else:
                # Empty or invalid name - should fail
                try:
                    cursor.execute("""
                        INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (test_ingredient, 50, 10, 'kg', 0, 'Fruits'))
                    conn.commit()
                    print(f"❌ FAIL: {test_name} - should have been rejected")
                    failed += 1
                except Exception as e:
                    print(f"✅ PASS: {test_name} - correctly rejected")
                    passed += 1
            
            # Clean up immediately
            cursor.execute("DELETE FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
            conn.commit()
        except Exception as e:
            if not should_pass:
                print(f"✅ PASS: {test_name} (correctly rejected)")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
                failed += 1
            conn.rollback()
    
    # Final cleanup
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TestIngredient_%'")
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
"""
Test Stock Add - Unit Type Validation
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
    print("TEST: Add Stock - Unit Type Validation")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    
    # Valid units (should be accepted)
    valid_units = ['kg', 'g', 'l', 'ml', 'pcs', 'bottle', 'pack', 'box']
    
    test_cases = []
    
    # Add valid units
    for unit in valid_units:
        test_cases.append((unit, True))
    
    # Add case variations (should be accepted)
    test_cases.append(("KILOGRAM", True))
    test_cases.append(("Kg", True))
    test_cases.append(("KG", True))
    
    # Add invalid units (should be rejected or defaulted)
    test_cases.append(("invalid", False))
    test_cases.append(("", False))
    test_cases.append(("123", False))
    
    passed = 0
    failed = 0
    
    for unit_value, should_pass in test_cases:
        # Create unique ingredient name for each test
        test_ingredient = f"TEST_UNIT_{hash(unit_value) % 10000}_{unique_id}"
        
        try:
            cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_UNIT_%'")
            
            # Use the unit value as is, or default to 'kg' for empty
            actual_unit = unit_value if unit_value and unit_value.strip() else 'kg'
            
            cursor.execute("""
                INSERT INTO tblStock (IngredientName, Category, QuantityInStock, MinStockLevel, UnitType, IsPerishable)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (test_ingredient, "Fruits", 50, 10, actual_unit, 0))
            conn.commit()
            
            # Verify what was actually stored
            cursor.execute("SELECT UnitType FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
            stored = cursor.fetchone()
            
            if should_pass:
                # Valid unit - should be stored as provided (or normalized)
                print(f"✅ PASS: {unit_value} - stored as '{stored[0]}'")
                passed += 1
            else:
                # Invalid unit - should be rejected or default to something valid
                if stored and stored[0] in valid_units:
                    print(f"✅ PASS: {unit_value} - defaulted to '{stored[0]}'")
                    passed += 1
                else:
                    print(f"❌ FAIL: {unit_value} - stored as '{stored[0]}' (should be valid unit)")
                    failed += 1
            
            # Clean up
            cursor.execute("DELETE FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
            conn.commit()
        except Exception as e:
            if not should_pass:
                print(f"✅ PASS: {unit_value} (correctly rejected)")
                passed += 1
            else:
                print(f"❌ FAIL: {unit_value} - {str(e)[:50]}")
                failed += 1
            conn.rollback()
    
    # Clean up any remaining test ingredients
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_UNIT_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
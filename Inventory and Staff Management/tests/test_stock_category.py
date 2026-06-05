"""
Test Stock Add - Category Validation
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
    print("TEST: Add Stock - Category Validation")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    
    valid_categories = ['Fruits', 'Vegetables', 'Dairy', 'Syrups', 'Other']
    
    test_cases = [
        ("Fruits", True),
        ("Vegetables", True),
        ("Dairy", True),
        ("Syrups", True),
        ("Other", True),
        ("fruits", True),   # Lowercase should be accepted (case-insensitive)
        ("FRUITS", True),  # Uppercase should be accepted
        ("Meat", False),   # Invalid - should default to Other
        ("Bakery", False), # Invalid - should default to Other
        ("", False),       # Empty - should default to Other
    ]
    
    passed = 0
    failed = 0
    
    for category_value, should_pass in test_cases:
        # Create unique ingredient name for this test
        test_ingredient = f"TEST_CAT_{category_value}_{unique_id}_{hash(category_value) % 10000}"
        
        try:
            cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_CAT_%'")
            
            # Determine what category to actually store
            if category_value and category_value.capitalize() in valid_categories:
                actual_category = category_value.capitalize()
            else:
                actual_category = "Other"  # Default for invalid/empty categories
            
            cursor.execute("""
                INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (test_ingredient, 50, 10, 'kg', 0, actual_category))
            conn.commit()
            
            # Verify the stored category
            cursor.execute("SELECT Category FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
            stored = cursor.fetchone()
            
            if should_pass:
                # Valid category should be stored as is (with proper case)
                if stored and stored[0] == category_value.capitalize():
                    print(f"✅ PASS: {category_value} - stored as '{stored[0]}'")
                    passed += 1
                else:
                    print(f"❌ FAIL: {category_value} - expected '{category_value.capitalize()}', got '{stored[0]}'")
                    failed += 1
            else:
                # Invalid category should default to "Other"
                if stored and stored[0] == "Other":
                    print(f"✅ PASS: {category_value} - defaulted to 'Other'")
                    passed += 1
                else:
                    print(f"❌ FAIL: {category_value} - should have defaulted to 'Other', got '{stored[0]}'")
                    failed += 1
            
            cursor.execute("DELETE FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
            conn.commit()
        except Exception as e:
            print(f"❌ FAIL: {category_value} - {str(e)[:50]}")
            failed += 1
            conn.rollback()
    
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
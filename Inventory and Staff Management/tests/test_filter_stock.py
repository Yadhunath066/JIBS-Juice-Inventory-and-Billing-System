"""
Test Filter Stock by Category
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
    print("TEST: Filter Stock by Category")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    
    # Create test stock items with different categories (using unique names)
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_CAT_FILTER_%'")
    
    test_stock = [
        (f"Apple_{unique_id}", "Fruits"),
        (f"Banana_{unique_id}", "Fruits"),
        (f"Spinach_{unique_id}", "Vegetables"),
        (f"Carrot_{unique_id}", "Vegetables"),
        (f"Almond_Milk_{unique_id}", "Dairy"),
    ]
    
    for name, category in test_stock:
        cursor.execute("""
            INSERT INTO tblStock (IngredientName, Category, QuantityInStock, MinStockLevel, UnitType, IsPerishable)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (f"TEST_CAT_FILTER_{name}", category, 50, 10, 'kg', 1))
    conn.commit()
    
    test_cases = [
        ("Filter Fruits", "Fruits", 2),
        ("Filter Vegetables", "Vegetables", 2),
        ("Filter Dairy", "Dairy", 1),
        ("Filter Invalid", "Meat", 0),
        ("No filter", "all", 5),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, category, expected_count in test_cases:
        if category == "all":
            cursor.execute("SELECT * FROM tblStock WHERE IngredientName LIKE 'TEST_CAT_FILTER_%'")
        else:
            cursor.execute("SELECT * FROM tblStock WHERE Category = %s AND IngredientName LIKE 'TEST_CAT_FILTER_%'", (category,))
        results = cursor.fetchall()
        actual_count = len(results)
        
        if actual_count == expected_count:
            print(f"✅ PASS: {test_name} - found {actual_count} results")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name} - expected {expected_count}, got {actual_count}")
            failed += 1
    
    # Clean up
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_CAT_FILTER_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
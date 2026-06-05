"""
Test Low Stock View Functionality
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
    print("TEST: Low Stock View Functionality")
    print("=" * 70)
    
    # Create unique ID for this test run
    unique_id = uuid.uuid4().hex[:6]
    
    # Create test stock items with different stock levels (using unique names)
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_LOW_%'")
    
    test_stock = [
        (f"TEST_LOW_Apple_{unique_id}", 50, 10),      # Above threshold
        (f"TEST_LOW_Banana_{unique_id}", 8, 10),      # Below threshold
        (f"TEST_LOW_Orange_{unique_id}", 3, 10),      # Below threshold
        (f"TEST_LOW_Mango_{unique_id}", 10, 10),      # Equal to threshold
    ]
    
    for name, quantity, min_level in test_stock:
        cursor.execute("""
            INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, quantity, min_level, 'kg', 0, 'Fruits'))
    conn.commit()
    
    # Query low stock items (QuantityInStock < MinStockLevel)
    cursor.execute("SELECT * FROM tblStock WHERE QuantityInStock < MinStockLevel AND IngredientName LIKE 'TEST_LOW_%'")
    low_stock_items = cursor.fetchall()
    
    expected_count = 2  # Banana and Orange should be low stock
    actual_count = len(low_stock_items)
    
    if actual_count == expected_count:
        print(f"✅ PASS: Low stock view shows {actual_count} items (expected {expected_count})")
        passed = 1
    else:
        print(f"❌ FAIL: Low stock view shows {actual_count} items (expected {expected_count})")
        passed = 0
    
    # Print which items are low stock for debugging
    print("\nLow stock items found:")
    for item in low_stock_items:
        print(f"  - {item[1]}: {item[2]} units (min: {item[3]})")
    
    # Clean up
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_LOW_%'")
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {0 if passed else 1}")
    return passed, 0 if passed else 1

if __name__ == "__main__":
    run_test()
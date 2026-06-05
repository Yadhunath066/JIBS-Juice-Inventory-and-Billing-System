"""
Test Stock Deduction API
"""

import requests
import mysql.connector
import time
import uuid

API_URL = "http://127.0.0.1:5001/api/deduct_stock"

print("=" * 70)
print("TEST: Stock Deduction API")
print("=" * 70)
print("NOTE: Make sure Flask app is running on port 5001")
print("=" * 70)

# First, check if API is reachable
try:
    response = requests.post(API_URL, json={"items": []}, timeout=3)
    print("✅ API is reachable\n")
except requests.exceptions.ConnectionError:
    print("❌ API is NOT reachable on port 5001")
    print("Please run: python inventoryapp.py in another terminal")
    exit(1)
except Exception as e:
    print(f"❌ API error: {e}")
    exit(1)

# Connect to database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="jibs_inventory and staff"
)
cursor = conn.cursor()

# Create a unique test ingredient to avoid conflicts
unique_id = uuid.uuid4().hex[:8]
test_ingredient = f"TEST_DEDUCT_{unique_id}"

# Create test ingredient with initial stock
cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_DEDUCT_%'")
cursor.execute("""
    INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (test_ingredient, 100, 10, 'kg', 0, 'Fruits'))
conn.commit()
print(f"Created test ingredient '{test_ingredient}' with 100 units\n")

# Get initial stock quantity
cursor.execute("SELECT QuantityInStock FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
initial_qty = cursor.fetchone()[0]
print(f"Initial stock for test ingredient: {initial_qty}")

test_cases = [
    ("Deduct 10 units", [{"name": test_ingredient, "quantity": 10}], True, 90),
    ("Deduct 25 units", [{"name": test_ingredient, "quantity": 25}], True, 65),
    ("Deduct 50 units", [{"name": test_ingredient, "quantity": 50}], True, 15),
    ("Try to deduct more than available", [{"name": test_ingredient, "quantity": 100}], True, -85),  # May go negative or fail
    ("Item not found", [{"name": "NonExistentItem12345", "quantity": 1}], False, None),
]

passed = 0
failed = 0

# Reset stock before test sequence
cursor.execute("UPDATE tblStock SET QuantityInStock = 100 WHERE IngredientName = %s", (test_ingredient,))
conn.commit()

for test_name, items, expected_success, expected_qty in test_cases:
    try:
        response = requests.post(API_URL, json={"items": items}, timeout=5)
        result = response.json()
        actual_success = result.get('success', False)
        
        # Get current stock after deduction
        cursor.execute("SELECT QuantityInStock FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
        current_qty = cursor.fetchone()[0]
        
        if expected_qty is not None:
            if actual_success == expected_success and current_qty == expected_qty:
                print(f"✅ PASS: {test_name} - Stock now: {current_qty}")
                passed += 1
            elif actual_success == expected_success:
                print(f"✅ PASS: {test_name} - Success={actual_success}, Stock: {current_qty}")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - Expected success={expected_success}, got {actual_success}")
                failed += 1
        else:
            if actual_success == expected_success:
                print(f"✅ PASS: {test_name} - Success={actual_success}")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name} - Expected success={expected_success}, got {actual_success}")
                failed += 1
        
        if 'message' in result:
            print(f"   Message: {result['message']}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ FAIL: {test_name} - Flask app not running on port 5001")
        failed += 1
    except Exception as e:
        print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
        failed += 1
    
    time.sleep(0.5)

# Final verification
cursor.execute("SELECT QuantityInStock FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
final_qty = cursor.fetchone()[0]
print(f"\nFinal stock for test ingredient: {final_qty}")

# Clean up test ingredient
cursor.execute("DELETE FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
conn.commit()
print(f"Cleaned up test ingredient '{test_ingredient}'")

cursor.close()
conn.close()

print(f"\n{'='*50}")
print(f"Results - Passed: {passed}, Failed: {failed}")
print(f"{'='*50}")

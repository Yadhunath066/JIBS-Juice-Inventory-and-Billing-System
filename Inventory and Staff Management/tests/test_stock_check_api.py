"""
Test Stock Check API
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:5001/api/check_stock"

print("=" * 70)
print("TEST: Stock Check API")
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

# Get actual stock quantities from database to make tests accurate
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="jibs_inventory and staff"
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT QuantityInStock FROM tblStock WHERE IngredientName = 'Apple'")
    apple_stock = cursor.fetchone()
    apple_qty = apple_stock[0] if apple_stock else 50
    
    cursor.execute("SELECT QuantityInStock FROM tblStock WHERE IngredientName = 'Banana'")
    banana_stock = cursor.fetchone()
    banana_qty = banana_stock[0] if banana_stock else 30
    
    conn.close()
    
    print(f"Current stock - Apple: {apple_qty}, Banana: {banana_qty}\n")
    
except Exception as e:
    print(f"Could not get stock quantities: {e}")
    apple_qty = 50
    banana_qty = 30

test_cases = [
    ("Valid stock - Apple", [{"name": "Apple", "quantity": min(5, apple_qty)}], True),
    ("Valid stock - Banana", [{"name": "Banana", "quantity": min(3, banana_qty)}], True),
    ("Insufficient stock", [{"name": "Apple", "quantity": apple_qty + 100}], False),
    ("Multiple items - all available", 
     [{"name": "Apple", "quantity": min(5, apple_qty)}, {"name": "Banana", "quantity": min(3, banana_qty)}], True),
    ("Multiple items - one insufficient", 
     [{"name": "Apple", "quantity": min(5, apple_qty)}, {"name": "Banana", "quantity": banana_qty + 100}], False),
    ("Item not found", [{"name": "NonExistentItem12345", "quantity": 1}], False),
    ("Empty items list", [], True),
    ("Zero quantity", [{"name": "Apple", "quantity": 0}], True),
]

passed = 0
failed = 0

for test_name, items, expected in test_cases:
    try:
        response = requests.post(API_URL, json={"items": items}, timeout=5)
        result = response.json()
        actual = result.get('available', False)
        
        if actual == expected:
            print(f"✅ PASS: {test_name}")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name} - expected {expected}, got {actual}")
            failed += 1
            if 'message' in result:
                print(f"   Message: {result['message']}")
    except requests.exceptions.ConnectionError:
        print(f"❌ FAIL: {test_name} - Flask app not running on port 5001")
        failed += 1
    except Exception as e:
        print(f"❌ FAIL: {test_name} - {str(e)[:50]}")
        failed += 1
    
    time.sleep(0.3)  # Small delay between requests

print(f"\n{'='*50}")
print(f"Results - Passed: {passed}, Failed: {failed}")
print(f"{'='*50}")
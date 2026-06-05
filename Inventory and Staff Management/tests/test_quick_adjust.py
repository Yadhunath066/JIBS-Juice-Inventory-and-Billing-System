"""
Test Quick Adjust Stock Quantity (+/- buttons)
"""

import mysql.connector
import requests
import time
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
    print("TEST: Quick Adjust Stock Quantity (+/- buttons)")
    print("=" * 70)
    print("NOTE: Make sure Flask app is running on port 5001")
    print("NOTE: You need to be logged in for this API to work")
    print("=" * 70)
    
    # First, login to get session cookie
    login_url = "http://127.0.0.1:5001/login"
    session = requests.Session()
    
    try:
        # Login first
        login_data = {
            'username': 'yadhunath',
            'password': 'admin123'
        }
        login_response = session.post(login_url, data=login_data)
        print("✅ Logged in successfully")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return 0, 1
    
    # Create unique test ingredient
    unique_id = uuid.uuid4().hex[:8]
    test_ingredient = f"TEST_QUICK_ADJUST_{unique_id}"
    
    cursor.execute("DELETE FROM tblStock WHERE IngredientName LIKE 'TEST_QUICK_ADJUST%'")
    cursor.execute("""
        INSERT INTO tblStock (IngredientName, QuantityInStock, MinStockLevel, UnitType, IsPerishable, Category)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (test_ingredient, 10, 5, 'kg', 0, 'Fruits'))
    conn.commit()
    
    cursor.execute("SELECT StockID FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
    stock_id = cursor.fetchone()[0]
    
    API_URL = f"http://127.0.0.1:5001/stock/quick-update/{stock_id}"
    
    test_cases = [
        ("Increase from 10 to 11", 10, 1, 11),
        ("Decrease from 11 to 10", 11, -1, 10),
        ("Decrease to zero", 1, -1, 0),
        ("Try negative - should stay at 0", 0, -1, 0),
        ("Large increase", 10, 100, 110),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, start_qty, change, expected in test_cases:
        # Set initial quantity
        cursor.execute("UPDATE tblStock SET QuantityInStock = %s WHERE StockID = %s", (start_qty, stock_id))
        conn.commit()
        
        new_qty = start_qty + change
        if new_qty < 0:
            new_qty = 0
        
        # Call API with session (maintains login)
        try:
            response = session.post(API_URL, json={"quantity": new_qty}, timeout=5)
            
            # Check if response is JSON
            try:
                result = response.json()
                actual_success = result.get('success', False)
            except:
                # If not JSON, check status code
                if response.status_code == 302:  # Redirect to login
                    print(f"❌ API Error for {test_name}: Not authenticated - try logging in first")
                    actual_success = False
                else:
                    print(f"❌ API Error for {test_name}: {response.text[:100]}")
                    actual_success = False
        
        except Exception as e:
            print(f"❌ API Error for {test_name}: {e}")
            actual_success = False
        
        # Verify database
        cursor.execute("SELECT QuantityInStock FROM tblStock WHERE StockID = %s", (stock_id,))
        db_qty = cursor.fetchone()[0]
        
        if db_qty == expected:
            print(f"✅ PASS: {test_name} - from {start_qty} to {db_qty}")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name} - expected {expected}, got {db_qty}")
            failed += 1
        
        time.sleep(0.5)
    
    # Clean up
    cursor.execute("DELETE FROM tblStock WHERE IngredientName = %s", (test_ingredient,))
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nResults - Passed: {passed}, Failed: {failed}")
    return passed, failed

if __name__ == "__main__":
    run_test()
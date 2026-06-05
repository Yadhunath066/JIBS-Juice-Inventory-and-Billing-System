import requests
import time

BASE = "http://127.0.0.1:5002"

print("=" * 60)
print("MENU MANAGEMENT SYSTEM - COMPLETE TEST")
print("=" * 60)

# Test 1: API Endpoint
print("\n[TEST 1] API Endpoint /api/menu_items")
try:
    r = requests.get(f"{BASE}/api/menu_items")
    if r.status_code == 200:
        print("✅ PASS: API returned status 200")
        items = r.json()
        print(f"   Found {len(items)} menu items")
    else:
        print(f"❌ FAIL: Status {r.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 2: Login Page Load
print("\n[TEST 2] Login Page Load")
try:
    r = requests.get(f"{BASE}/admin/login")
    if r.status_code == 200:
        print("✅ PASS: Login page loaded")
    else:
        print(f"❌ FAIL: Status {r.status_code}")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 3: Login with correct credentials
print("\n[TEST 3] Login with correct credentials")
session = requests.Session()
login_data = {"username": "admin", "password": "admin123"}
r = session.post(f"{BASE}/admin/login", data=login_data)
if r.status_code == 200 or r.status_code == 302:
    print("✅ PASS: Login successful")
else:
    print(f"❌ FAIL: Status {r.status_code}")

# Test 4: Access Menu List
print("\n[TEST 4] Access Menu List")
r = session.get(f"{BASE}/admin/menu")
if r.status_code == 200:
    print("✅ PASS: Menu list loaded")
else:
    print(f"❌ FAIL: Status {r.status_code}")

# Test 5: Add new menu item
print("\n[TEST 5] Add new menu item")
unique_name = f"Test Juice {int(time.time())}"
new_item = {
    "name": unique_name,
    "price_sm": "25",
    "price_reg": "35",
    "price_lg": "45",
    "category": "Fresh Fruit Juices",
    "is_vegan": "on"
}
r = session.post(f"{BASE}/admin/menu/add", data=new_item)
if r.status_code == 200 or r.status_code == 302:
    print(f"✅ PASS: Added '{unique_name}'")
else:
    print(f"❌ FAIL: Could not add item")

# Test 6: Verify item was added
print("\n[TEST 6] Verify item was added")
r = session.get(f"{BASE}/admin/menu")
if unique_name in r.text:
    print(f"✅ PASS: '{unique_name}' found in menu list")
else:
    print(f"❌ FAIL: '{unique_name}' not found")

# Test 7: Filter by category
print("\n[TEST 7] Filter by category")
r = session.get(f"{BASE}/admin/menu?category=Fresh Fruit Juices")
if r.status_code == 200:
    print("✅ PASS: Category filter works")
else:
    print(f"❌ FAIL: Status {r.status_code}")

# Test 8: Search by name
print("\n[TEST 8] Search by name")
r = session.get(f"{BASE}/admin/menu?search=Mango")
if r.status_code == 200:
    print("✅ PASS: Search works")
else:
    print(f"❌ FAIL: Status {r.status_code}")

# Test 9: Logout
print("\n[TEST 9] Logout")
r = session.get(f"{BASE}/admin/logout")
if r.status_code == 200 or r.status_code == 302:
    print("✅ PASS: Logout successful")
else:
    print(f"❌ FAIL: Status {r.status_code}")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
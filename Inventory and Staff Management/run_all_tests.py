"""
RUN ALL TESTS - JIBS Inventory System
Simplified master script to execute all test scripts
"""

import subprocess
import sys
import os

print("=" * 80)
print(" JIBS INVENTORY SYSTEM - FULL TEST SUITE")
print("=" * 80)
print(" Make sure your Flask app is running on port 5001")
print(" In another terminal, run: python inventoryapp.py")
print("=" * 80)

# List of all test scripts
test_scripts = [
    "test_stock_quantity.py",
    "test_stock_minlevel.py",
    "test_stock_name.py",
    "test_stock_unit.py",
    "test_stock_category.py",
    "test_staff_username.py",
    "test_staff_password.py",
    "test_staff_role.py",
    "test_staff_edit.py",
    "test_staff_delete_gdpr.py",
    "test_login.py",
    "test_search_staff.py",
    "test_filter_staff.py",
    "test_search_stock.py",
    "test_filter_stock.py",
    "test_quick_adjust.py",
    "test_low_stock_view.py",
    "test_stock_check_api.py",
    "test_stock_deduct_api.py",
]

total_passed = 0
total_failed = 0

for script in test_scripts:
    script_path = os.path.join("tests", script)
    
    if not os.path.exists(script_path):
        print(f"\n❌ File not found: {script_path}")
        continue
    
    print(f"\n{'='*60}")
    print(f"Running: {script}")
    print('='*60)
    
    # Run the test script directly and show output
    result = subprocess.run([sys.executable, script_path], capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"\n✅ {script} completed successfully")
    else:
        print(f"\n❌ {script} had errors")

print("\n" + "=" * 80)
print(" TEST COMPLETED")
print("=" * 80)
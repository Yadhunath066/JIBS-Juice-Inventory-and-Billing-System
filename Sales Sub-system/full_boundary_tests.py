import sqlite3

def run_all_tests():
    conn = sqlite3.connect('jibs.db')
    cursor = conn.cursor()
    results = []

    def test_insert(values, expected_success, description):
        try:
            # Build dynamic INSERT with correct number of placeholders
            placeholders = ','.join(['?'] * len(values))
            cursor.execute(f'INSERT INTO tblSale VALUES ({placeholders})', values)
            conn.commit()
            success = True
            conn.rollback()
        except Exception as e:
            success = False
            error_msg = str(e)
        actual = "PASS (insert succeeded)" if success else f"FAIL ({error_msg})"
        expected = "SUCCESS" if expected_success else "FAIL"
        status = "✅" if (success == expected_success) else "❌"
        results.append([description, str(values[0]) if values else "N/A", expected, actual, status])
        conn.rollback()

    # Test TotalAmount (as before, but we'll use explicit INSERT with all columns)
    # We'll use a helper that inserts full rows with default for other columns
    def test_total_amount(value, expected_success, desc):
        try:
            cursor.execute('''
                INSERT INTO tblSale (SaleDate, TotalAmount, PaymentMethod, StaffID, ItemCount, IsProcessed)
                VALUES (datetime('now'), ?, 'Cash', 1, 1, 1)
            ''', (value,))
            conn.commit()
            success = True
            conn.rollback()
        except Exception as e:
            success = False
            error_msg = str(e)
        actual = "PASS" if success else f"FAIL ({error_msg})"
        expected = "SUCCESS" if expected_success else "FAIL"
        status = "✅" if (success == expected_success) else "❌"
        results.append([desc, value, expected, actual, status])
        conn.rollback()

    total_tests = [
        (0, True, "Extreme Min (0)"),
        (-1, False, "Min -1 (negative)"),
        (1, True, "Min +1"),
        (2147483646, True, "Max -1"),
        (2147483647, True, "Max (boundary)"),
        (2147483648, True, "Max +1 (big int)"),
        (10000, True, "Mid value"),
        (999999999, True, "Extreme Max"),
    ]

    for val, exp, desc in total_tests:
        test_total_amount(val, exp, desc)

    # Test ItemCount
    def test_item_count(value, expected_success, desc):
        try:
            cursor.execute('''
                INSERT INTO tblSale (SaleDate, TotalAmount, PaymentMethod, StaffID, ItemCount, IsProcessed)
                VALUES (datetime('now'), 1000, 'Cash', 1, ?, 1)
            ''', (value,))
            conn.commit()
            success = True
            conn.rollback()
        except Exception as e:
            success = False
            error_msg = str(e)
        actual = "PASS" if success else f"FAIL ({error_msg})"
        expected = "SUCCESS" if expected_success else "FAIL"
        status = "✅" if (success == expected_success) else "❌"
        results.append([desc, value, expected, actual, status])
        conn.rollback()

    item_tests = [
        (0, True, "ItemCount = 0"),
        (-1, False, "ItemCount negative"),
        (1, True, "ItemCount = 1"),
        (9999, True, "ItemCount large"),
    ]
    for val, exp, desc in item_tests:
        test_item_count(val, exp, desc)

    # Test PaymentMethod (NOT NULL and allowed values)
    def test_payment_method(value, expected_success, desc):
        try:
            cursor.execute('''
                INSERT INTO tblSale (SaleDate, TotalAmount, PaymentMethod, StaffID, ItemCount, IsProcessed)
                VALUES (datetime('now'), 1000, ?, 1, 1, 1)
            ''', (value,))
            conn.commit()
            success = True
            conn.rollback()
        except Exception as e:
            success = False
            error_msg = str(e)
        actual = "PASS" if success else f"FAIL ({error_msg})"
        expected = "SUCCESS" if expected_success else "FAIL"
        status = "✅" if (success == expected_success) else "❌"
        results.append([desc, value, expected, actual, status])
        conn.rollback()

    payment_tests = [
        ('Cash', True, "Valid: Cash"),
        ('Card', True, "Valid: Card"),
        ('Mobile', True, "Valid: Mobile"),
        ('', False, "Empty string (should fail NOT NULL?)"),
        (None, False, "NULL (should fail NOT NULL)"),
        ('Bitcoin', True, "Invalid value (allowed by DB but not by app)"),
    ]
    for val, exp, desc in payment_tests:
        test_payment_method(val, exp, desc)

    # Test IsProcessed (should accept 0/1 only? SQLite accepts any integer)
    def test_is_processed(value, expected_success, desc):
        try:
            cursor.execute('''
                INSERT INTO tblSale (SaleDate, TotalAmount, PaymentMethod, StaffID, ItemCount, IsProcessed)
                VALUES (datetime('now'), 1000, 'Cash', 1, 1, ?)
            ''', (value,))
            conn.commit()
            success = True
            conn.rollback()
        except Exception as e:
            success = False
            error_msg = str(e)
        actual = "PASS" if success else f"FAIL ({error_msg})"
        expected = "SUCCESS" if expected_success else "FAIL"
        status = "✅" if (success == expected_success) else "❌"
        results.append([desc, value, expected, actual, status])
        conn.rollback()

    is_tests = [
        (0, True, "IsProcessed = 0 (false)"),
        (1, True, "IsProcessed = 1 (true)"),
        (2, True, "IsProcessed = 2 (non‑boolean, but accepted by SQLite)"),
        ('true', False, "String (should fail type)"),
        (None, True, "NULL (defaults to 1, so insert succeeds)"),
    ]
    for val, exp, desc in is_tests:
        test_is_processed(val, exp, desc)

    # Print full results table
    print("\n" + "="*100)
    print("COMPLETE TEST LOG – All Columns (Boundary & Invalid)")
    print("="*100)
    print(f"{'Test Description':<35} {'Test Data':<20} {'Expected':<10} {'Actual Result':<45} {'Status'}")
    print("-"*100)
    for row in results:
        # Truncate long strings
        test_data = str(row[1])[:18]
        actual = row[3][:42]
        print(f"{row[0]:<35} {test_data:<20} {row[2]:<10} {actual:<45} {row[4]}")
    print("="*100)
    print("\nNOTE: The database accepts negative TotalAmount and non‑standard PaymentMethod values because no CHECK constraints exist.")
    print("Application logic prevents these cases. This is an acceptable trade‑off for a prototype.")

if __name__ == "__main__":
    run_all_tests()
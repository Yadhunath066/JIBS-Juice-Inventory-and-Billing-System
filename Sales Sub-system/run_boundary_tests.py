import sqlite3

def run_tests():
    conn = sqlite3.connect('jibs.db')
    cursor = conn.cursor()
    results = []

    # Helper to execute a test and return result
    def test_insert(values, expected_success, description):
        try:
            cursor.execute('''
                INSERT INTO tblSale (TotalAmount, PaymentMethod, ItemCount, IsProcessed)
                VALUES (?, ?, ?, ?)
            ''', values)
            conn.commit()
            success = True
            # Rollback to keep database clean
            conn.rollback()
        except Exception as e:
            success = False
            error_msg = str(e)
        actual = "PASS (insert succeeded)" if success else f"FAIL ({error_msg})"
        expected = "SUCCESS" if expected_success else "FAIL"
        status = "✅" if (success == expected_success) else "❌"
        results.append([description, values[0], expected, actual, status])
        # Rollback anyway
        conn.rollback()

    # Test cases for TotalAmount
    test_cases = [
        (0, 'Cash', 1, 1, True, "Extreme Min (0)"),
        (-1, 'Cash', 1, 1, False, "Min -1 (negative)"),
        (1, 'Cash', 1, 1, True, "Min +1"),
        (2147483646, 'Cash', 1, 1, True, "Max -1"),
        (2147483647, 'Cash', 1, 1, True, "Max (boundary)"),
        (2147483648, 'Cash', 1, 1, True, "Max +1 (SQLite handles big ints)"),
        (10000, 'Cash', 1, 1, True, "Mid value"),
        (999999999, 'Cash', 1, 1, True, "Extreme Max"),
    ]

    for total, pay, count, proc, expected_success, desc in test_cases:
        test_insert((total, pay, count, proc), expected_success, desc)

    # Print table
    print("\n" + "="*80)
    print("TEST LOG – TotalAmount column (boundary & invalid)")
    print("="*80)
    print(f"{'Test Type':<20} {'Test Data':<15} {'Expected':<10} {'Actual Result':<40} {'Status'}")
    print("-"*80)
    for row in results:
        print(f"{row[0]:<20} {row[1]:<15} {row[2]:<10} {row[3]:<40} {row[4]}")
    print("="*80)

if __name__ == "__main__":
    run_tests()
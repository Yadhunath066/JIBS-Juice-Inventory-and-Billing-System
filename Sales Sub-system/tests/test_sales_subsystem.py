"""
Test script for JIBS Sales Sub-system
Tests boundary values for TotalAmount, ItemCount, PaymentMethod, IsProcessed
Compatible with MySQL database
"""

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="jibs_db"
    )

def run_all_tests():
    conn = get_db_connection()
    cursor = conn.cursor()
    results = []

    def test_insert(sql, values, expected_success, description):
        try:
            cursor.execute(sql, values)
            conn.commit()
            success = True
            conn.rollback()
        except Exception as e:
            success = False
            error_msg = str(e)
        actual = "PASS" if success else f"FAIL ({error_msg})"
        expected = "SUCCESS" if expected_success else "FAIL"
        status = "PASS" if (success == expected_success) else "FAIL"
        results.append([description, str(values[0]) if values else "N/A", expected, actual, status])
        conn.rollback()

    # Test TotalAmount
    total_tests = [
        (0, True, "Extreme Min (0)"),
        (-1, True, "Min -1 (negative)"),
        (1, True, "Min +1"),
        (2147483646, True, "Max -1"),
        (2147483647, True, "Max (boundary)"),
        (10000, True, "Mid value"),
        (999999999, True, "Extreme Max"),
    ]
    for val, exp, desc in total_tests:
        sql = "INSERT INTO tblSale (TotalAmount, PaymentMethod, ItemCount) VALUES (%s, 'Cash', 1)"
        test_insert(sql, (val,), exp, desc)

    # Test ItemCount
    item_tests = [
        (0, True, "ItemCount = 0"),
        (-1, True, "ItemCount negative"),
        (1, True, "ItemCount = 1"),
        (9999, True, "ItemCount large"),
    ]
    for val, exp, desc in item_tests:
        sql = "INSERT INTO tblSale (TotalAmount, PaymentMethod, ItemCount) VALUES (1000, 'Cash', %s)"
        test_insert(sql, (val,), exp, desc)

    # Test PaymentMethod
    payment_tests = [
        ('Cash', True, "Valid: Cash"),
        ('Card', True, "Valid: Card"),
        ('Mobile', True, "Valid: Mobile"),
        ('', True, "Empty string"),
        (None, False, "NULL value"),
        ('Bitcoin', True, "Invalid value (DB accepts, app rejects)"),
    ]
    for val, exp, desc in payment_tests:
        sql = "INSERT INTO tblSale (TotalAmount, PaymentMethod, ItemCount) VALUES (1000, %s, 1)"
        test_insert(sql, (val,), exp, desc)

    # Test IsProcessed
    processed_tests = [
       (0, True, "IsProcessed = 0"),
       (1, True, "IsProcessed = 1"),
       (2, True, "IsProcessed = 2"),
       ("true", True, "IsProcessed = 'true'"),
    ]

    for val, exp, desc in processed_tests:
       sql = """
       INSERT INTO tblSale
       (TotalAmount, PaymentMethod, ItemCount, IsProcessed)
       VALUES (1000, 'Cash', 1, %s)
       """
       test_insert(sql, (val,), exp, desc)

    # Print results
    print("\n" + "="*100)
    print("TEST LOG – Sales Sub-system Boundary Tests")
    print("="*100)
    print(f"{'Test Description':<35} {'Test Data':<20} {'Expected':<10} {'Actual Result':<45} {'Status'}")
    print("-"*100)
    for row in results:
        test_data = str(row[1])[:18]
        actual = row[3][:42]
        print(f"{row[0]:<35} {test_data:<20} {row[2]:<10} {actual:<45} {row[4]}")
    print("="*100)

if __name__ == "__main__":
    run_all_tests()
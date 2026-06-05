# Sales Sub-system Tests

This folder contains test scripts for the JIBS Sales Sub-system.

## Purpose

The tests verify:

* Boundary values for `TotalAmount` and `ItemCount`
* `PaymentMethod` validation (database vs application behaviour)
* `IsProcessed` default and type handling

## Relationship to Portfolio 2

The test results documented in **Portfolio 2 – Test Logs** were produced using this script.

## Notes on Test Results

* Some test records have NULL `StaffID` values because they were inserted directly using SQL for boundary testing. In normal system operation, every sale is linked to a valid staff member.
* The database accepts some values (e.g., negative `TotalAmount`, `'Bitcoin'` as `PaymentMethod`) that the application later prevents.
* The application validation layer prevents users from entering invalid values through the user interface.
* This behaviour is documented and considered acceptable for a university prototype.

## Running the Tests

1. Ensure MySQL is running (XAMPP).
2. Ensure database `jibs_db` exists.
3. Run:

python tests/test_sales_subsystem.py
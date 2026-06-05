# JIBS-Juice-Inventory-and-Billing-System
JIBS (Juice Inventory &amp; Billing System) – A full-stack web application for juice bar management. Includes billing, inventory tracking, stock deduction, order history, printable receipts, and role-based access. Built with Python Flask, MySQL, HTML/CSS/JS.

## Data Collection & Privacy

The JIBS Sales Sub-system stores the following order data in the database:
- Order items, sizes, quantities, prices (in øre)
- Total amount
- Payment method (Card, Cash, Mobile)
- Date and time of the order
- Staff ID (references the cashier)

**No customer names, email addresses, phone numbers, or card numbers are ever stored.**  
Orders are kept for 7 years to comply with UK tax laws (for sales records).  
The system does not collect any biometric data, location data, or unnecessary personal identifiers.

For card payments, the system only records the method ("Card") – no actual card details are processed or stored.


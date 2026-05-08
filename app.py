"""
JIBS Sales Sub-system - Sanjaya
Full menu with categories, sizes, and prices in DKK (øre).
Includes date-time range filter for order history.
Connects to Monika's menu API with fallback to hardcoded menu.
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime
import sqlite3
import requests  # Used to call Monika's menu API

app = Flask(__name__)
app.secret_key = 'jibs-secret-key-2026'

# ============ DATABASE SETUP ============

def get_db():
    """Establish connection to SQLite database"""
    return sqlite3.connect('jibs.db')

def init_db():
    """Create tblSale table if it doesn't exist (run once at startup)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tblSale (
            SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
            SaleDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            TotalAmount INTEGER NOT NULL,
            PaymentMethod TEXT,
            StaffID INTEGER,
            ItemCount INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ============ DATABASE HELPER FUNCTIONS ============

def get_all_orders():
    """Return all orders for order history page"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tblSale ORDER BY SaleDate DESC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def get_order_by_id(sale_id):
    """Find a single order by SaleID (used for search and details page)"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tblSale WHERE SaleID = ?", (sale_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_orders_by_datetime(from_datetime, to_datetime):
    """Filter orders by date-time range (used for advanced filter)"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tblSale 
        WHERE SaleDate BETWEEN ? AND ?
        ORDER BY SaleDate DESC
    """, (from_datetime, to_datetime))
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def save_order(total_amount, payment_method, staff_id, item_count):
    """Save order to database and return the new SaleID"""
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO tblSale (SaleDate, TotalAmount, PaymentMethod, StaffID, ItemCount)
        VALUES (?, ?, ?, ?, ?)
    ''', (now, total_amount, payment_method, staff_id, item_count))
    conn.commit()
    sale_id = cursor.lastrowid
    conn.close()
    return sale_id

# ============ MENU API INTEGRATION (Monika's API) ============

def get_menu_from_monika():
    """
    Fetch menu from Monika's API and convert to required format.
    Returns menu data grouped by category with prices in øre.
    Falls back to hardcoded menu if API is unavailable.
    """
    try:
        # Call Monika's menu API (running on port 5002)
        response = requests.get('http://127.0.0.1:5002/api/menu_items', timeout=5)
        if response.status_code == 200:
            items = response.json()
            # Convert from Monika's format to the format expected by menu.html
            # Monika's format: [{"name": "...", "sizes": {...}, "category": "..."}]
            # Required format: {"Category": [{"name": "...", "prices": {...}}]}
            menu_data = {}
            for item in items:
                category = item['category']
                if category not in menu_data:
                    menu_data[category] = []
                menu_data[category].append({
                    "name": item['name'],
                    "prices": item['sizes']  # sizes contains Sm, Reg, Lg prices in øre
                })
            return menu_data
    except Exception as e:
        # If API call fails, use fallback menu
        print(f"Error fetching menu from Monika's API: {e}")
    
    # Fallback to hardcoded menu if API fails
    return get_fallback_menu()

def get_fallback_menu():
    """Hardcoded menu as fallback when Monika's API is unavailable."""
    return {
        "Fresh Fruit Juices": [
            {"name": "Watermelon Juice", "prices": {"Sm": 2900, "Reg": 3900, "Lg": 4900}},
            {"name": "Mango Juice", "prices": {"Sm": 2900, "Reg": 3900, "Lg": 4900}},
            {"name": "Papaya Juice", "prices": {"Sm": 2900, "Reg": 3900, "Lg": 4900}},
            {"name": "Orange Juice", "prices": {"Sm": 2900, "Reg": 3900, "Lg": 4900}},
            {"name": "Pineapple Juice", "prices": {"Sm": 3200, "Reg": 4200, "Lg": 5200}},
            {"name": "Mixed Fruit Juice", "prices": {"Sm": 3500, "Reg": 4500, "Lg": 5500}},
        ],
        "Sugarcane Juice": [
            {"name": "Classic Sugarcane", "prices": {"Sm": 2500, "Reg": 3500, "Lg": 4500}},
            {"name": "Ginger Sugarcane", "prices": {"Sm": 2900, "Reg": 3900, "Lg": 4900}},
            {"name": "Mint Sugarcane", "prices": {"Sm": 2900, "Reg": 3900, "Lg": 4900}},
            {"name": "Lemon Sugarcane", "prices": {"Sm": 2900, "Reg": 3900, "Lg": 4900}},
        ],
        "Smoothies & Shakes": [
            {"name": "Mango Smoothie", "prices": {"Sm": 3900, "Reg": 5200, "Lg": 6500}},
            {"name": "Tropical Blast", "prices": {"Sm": 4200, "Reg": 5500, "Lg": 6800}},
            {"name": "Green Detox", "prices": {"Sm": 4200, "Reg": 5500, "Lg": 6800}},
            {"name": "Strawberry Shake", "prices": {"Sm": 4200, "Reg": 5500, "Lg": 6800}},
            {"name": "Banana Shake", "prices": {"Sm": 3900, "Reg": 5200, "Lg": 6500}},
            {"name": "Berry Mix Smoothie", "prices": {"Sm": 4500, "Reg": 5800, "Lg": 7200}},
        ]
    }

def find_item_price(name, size):
    """
    Get price for a given item name and size (Sm/Reg/Lg)
    Fetches menu from Monika's API to find the price.
    """
    menu_data = get_menu_from_monika()
    for category, items in menu_data.items():
        for item in items:
            if item["name"] == name and size in item["prices"]:
                return item["prices"][size]
    return None

# ============ CART FUNCTIONS ============

def get_cart_total(cart):
    """Calculate total amount in øre from cart items"""
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return total

def get_item_count(cart):
    """Calculate total number of items in cart"""
    return sum(item['quantity'] for item in cart.values())

# ============ LOGIN (Backlog 8) ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Cashier login page.
    Simple authentication for now. Will integrate Yadhunath's staff API later.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'cashier' and password == '123':
            session['staff_id'] = 1
            session['staff_name'] = 'Cashier'
            return redirect(url_for('main_menu'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clear session and redirect to login page"""
    session.clear()
    return redirect(url_for('login'))

# ============ MAIN MENU (Backlog 8) ============

@app.route('/')
@app.route('/main_menu')
def main_menu():
    """Dashboard with navigation cards for cashier"""
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    return render_template('main_menu.html', staff_name=session.get('staff_name'))

# ============ MENU DISPLAY (Calls Monika's API) ============

@app.route('/menu')
def menu():
    """
    Display juice menu with categories and size options.
    Fetches menu data from Monika's API dynamically.
    """
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    menu_data = get_menu_from_monika()  # Fetch menu from Monika's API
    return render_template('menu.html', menu=menu_data)

# ============ ADD TO CART (Backlog 1) - AJAX VERSION ============

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """
    Add item with selected size and quantity to cart via AJAX.
    Returns JSON instead of redirecting.
    """
    item_name = request.form.get('item_name')
    size = request.form.get('size')
    quantity = int(request.form.get('quantity', 1))
    
    # Validation: size must be selected
    if not size:
        return jsonify({'success': False, 'error': 'Please select a size'})
    
    # Get price from Monika's menu data
    price = find_item_price(item_name, size)
    if not price:
        return jsonify({'success': False, 'error': 'Item not found'})
    
    if 'cart' not in session:
        session['cart'] = {}
    
    # Create unique key combining item name and size
    cart_key = f"{item_name}_{size}"
    if cart_key in session['cart']:
        session['cart'][cart_key]['quantity'] += quantity
        session['cart'][cart_key]['line_total'] = session['cart'][cart_key]['price'] * session['cart'][cart_key]['quantity']
    else:
        session['cart'][cart_key] = {
            'name': item_name,
            'size': size,
            'price': price,
            'quantity': quantity,
            'line_total': price * quantity
        }
    session.modified = True
    
    # Return JSON success response
    return jsonify({'success': True, 'message': f'{quantity} x {item_name} ({size}) added to cart'})

# ============ CART COUNT (for badge) ============

@app.route('/cart_count')
def cart_count():
    """Return the total number of items in cart (for badge display)"""
    cart = session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return jsonify({'count': count})

# ============ CART PAGE ============

@app.route('/cart')
def cart():
    """Display current shopping cart with all items and total"""
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    if 'cart' not in session:
        session['cart'] = {}
    total = get_cart_total(session['cart'])
    return render_template('cart.html', cart=session['cart'], total=total)

# ============ UPDATE QUANTITY (Backlog 2) - AJAX ============

@app.route('/update_quantity/<string:cart_key>', methods=['POST'])
def update_quantity(cart_key):
    """
    Update item quantity via AJAX without page reload.
    If quantity becomes 0, item is removed from cart.
    """
    data = request.get_json()
    quantity = int(data.get('quantity', 0))
    if quantity <= 0:
        if cart_key in session['cart']:
            del session['cart'][cart_key]
    else:
        if cart_key in session['cart']:
            session['cart'][cart_key]['quantity'] = quantity
            session['cart'][cart_key]['line_total'] = session['cart'][cart_key]['price'] * quantity
    session.modified = True
    total = get_cart_total(session['cart'])
    return jsonify({'success': True, 'total': total})

# ============ REMOVE ITEM (Backlog 3) - AJAX ============

@app.route('/remove_item/<string:cart_key>', methods=['POST'])
def remove_item(cart_key):
    """Remove item from cart completely via AJAX"""
    if cart_key in session['cart']:
        del session['cart'][cart_key]
    session.modified = True
    total = get_cart_total(session['cart'])
    return jsonify({'success': True, 'total': total})

# ============ PLACE ORDER (Backlog 6) ============

@app.route('/place_order', methods=['POST'])
def place_order():
    """
    Save order to database, clear cart, and show success page.
    This is where Yadhunath's stock API will be called later.
    """
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('cart'))
    payment_method = request.form.get('payment_method')
    staff_id = session.get('staff_id', 1)
    total = get_cart_total(session['cart'])
    item_count = get_item_count(session['cart'])
    sale_id = save_order(total, payment_method, staff_id, item_count)
    session['cart'] = {}  # Clear cart after successful order
    session.modified = True
    return render_template('order_success.html', sale_id=sale_id)

# ============ ORDER HISTORY (Backlog 7) with DATE-TIME FILTER ============

@app.route('/order_history')
def order_history():
    """
    Show all orders or filter by date-time range.
    Supports custom date-time picker for advanced filtering.
    """
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    if from_date and to_date:
        # Convert HTML5 datetime-local format to SQLite format
        from_datetime = from_date.replace('T', ' ') + ':00'
        to_datetime = to_date.replace('T', ' ') + ':59'
        orders = get_orders_by_datetime(from_datetime, to_datetime)
    else:
        orders = get_all_orders()
    
    return render_template('order_history.html', orders=orders, error=None)

# ============ SEARCH BY SALEID (Backlog 9) ============

@app.route('/search_order')
def search_order():
    """Find and display a specific order by SaleID"""
    sale_id = request.args.get('sale_id')
    if sale_id and sale_id.isdigit():
        order = get_order_by_id(int(sale_id))
        if order:
            return render_template('order_details.html', order=order)
        else:
            orders = get_all_orders()
            return render_template('order_history.html', orders=orders, error=f"Order {sale_id} not found")
    return redirect(url_for('order_history'))

# ============ ORDER DETAILS ============

@app.route('/order_details/<int:sale_id>')
def order_details(sale_id):
    """Show detailed information for a single order"""
    order = get_order_by_id(sale_id)
    if order:
        return render_template('order_details.html', order=order)
    return redirect(url_for('order_history'))

# ============ ORDER TYPE (Backlog 5) - Front-end only ============

@app.route('/set_order_type', methods=['POST'])
def set_order_type():
    """
    Store order type in session for receipt display.
    NOT stored in database - only used for receipt and staff display.
    """
    data = request.get_json()
    session['order_type'] = data.get('order_type', 'takeaway')
    session.modified = True
    return jsonify({'success': True})

# ============ RUN THE APP ============

if __name__ == '__main__':
    app.run(debug=True, port=5000)
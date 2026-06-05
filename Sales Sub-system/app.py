"""
JIBS Sales Sub-system - Sanjaya
Full menu with categories, sizes, and prices in DKK (øre).
Includes date-time range filter for order history.
Connects to Monika's menu API with fallback to hardcoded menu.
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime
import mysql.connector
import requests

app = Flask(__name__, template_folder='.')
app.secret_key = 'jibs-secret-key-2026'

# ============ DATABASE SETUP (MySQL) ============

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="jibs_db"
    )

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tblSale (
            SaleID INT PRIMARY KEY AUTO_INCREMENT,
            SaleDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            TotalAmount INT NOT NULL,
            PaymentMethod VARCHAR(10) NOT NULL,
            StaffID INT,
            ItemCount INT NOT NULL,
            IsProcessed TINYINT DEFAULT 1
        )
    ''')
    # Also create tblSaleLine if needed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tblSaleLine (
            SaleLineID INT PRIMARY KEY AUTO_INCREMENT,
            SaleID INT,
            ItemID INT,
            ItemName VARCHAR(100),
            Quantity INT,
            LinePrice INT,
            FOREIGN KEY (SaleID) REFERENCES tblSale(SaleID)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ============ DATABASE HELPER FUNCTIONS ============

def get_all_orders():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblSale ORDER BY SaleDate DESC")
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_order_by_id(sale_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblSale WHERE SaleID = %s", (sale_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_orders_by_datetime(from_datetime, to_datetime):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM tblSale 
        WHERE SaleDate BETWEEN %s AND %s
        ORDER BY SaleDate DESC
    """, (from_datetime, to_datetime))
    orders = cursor.fetchall()
    conn.close()
    return orders

def save_order(total_amount, payment_method, staff_id, item_count):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO tblSale (SaleDate, TotalAmount, PaymentMethod, StaffID, ItemCount)
        VALUES (%s, %s, %s, %s, %s)
    ''', (now, total_amount, payment_method, staff_id, item_count))
    conn.commit()
    sale_id = cursor.lastrowid
    conn.close()
    return sale_id

# ============ MENU API INTEGRATION ============

def get_menu_from_monika():
    try:
        response = requests.get('http://127.0.0.1:5002/api/menu_items', timeout=5)
        if response.status_code == 200:
            items = response.json()
            menu_data = {}
            for item in items:
                category = item['category']
                if category not in menu_data:
                    menu_data[category] = []
                menu_data[category].append({
                    "name": item['name'],
                    "prices": item['sizes']
                })
            return menu_data
    except Exception as e:
        print(f"Error fetching menu from Monika's API: {e}")
    
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
    menu_data = get_menu_from_monika()
    for category, items in menu_data.items():
        for item in items:
            if item["name"] == name and size in item["prices"]:
                return item["prices"][size]
    return None

# ============ CART FUNCTIONS ============

def get_cart_total(cart):
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return total

def get_item_count(cart):
    return sum(item['quantity'] for item in cart.values())

# ============ LOGIN ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'cashier' and password == 'sanjaya123':
            session['staff_id'] = 1
            session['staff_name'] = 'Cashier'
            return redirect(url_for('main_menu'))
        else:
            return render_template('s_login.html', error='The username or password you entered is incorrect. Please try again later.')
    return render_template('s_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#=========forgot password ==========
@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

# ============ MAIN MENU ============

@app.route('/')
@app.route('/main_menu')
def main_menu():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    return render_template('main_menu.html', staff_name=session.get('staff_name'))

# ============ MENU DISPLAY ============

@app.route('/menu')
def menu():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    menu_data = get_menu_from_monika()
    return render_template('s_menu.html', menu=menu_data)

# ============ ADD TO CART (AJAX) ============

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item_name')
    size = request.form.get('size')
    quantity = int(request.form.get('quantity', 1))
    
    if not size:
        return jsonify({'success': False, 'error': 'Please select a size'})
    
    price = find_item_price(item_name, size)
    if not price:
        return jsonify({'success': False, 'error': 'Item not found'})
    
    if 'cart' not in session:
        session['cart'] = {}
    
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
    
    return jsonify({'success': True, 'message': f'{quantity} x {item_name} ({size}) added to cart'})

# ============ CLEAR CART ============

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = {}
    session.modified = True
    return jsonify({'success': True})

# ============ CART COUNT ============

@app.route('/cart_count')
def cart_count():
    cart = session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return jsonify({'count': count})

# ============ CART PAGE ============

@app.route('/cart')
def cart():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    if 'cart' not in session:
        session['cart'] = {}
    total = get_cart_total(session['cart'])
    return render_template('cart.html', cart=session['cart'], total=total)

# ============ UPDATE QUANTITY (AJAX) ============

@app.route('/update_quantity/<string:cart_key>', methods=['POST'])
def update_quantity(cart_key):
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

# ============ REMOVE ITEM (AJAX) ============

@app.route('/remove_item/<string:cart_key>', methods=['POST'])
def remove_item(cart_key):
    if cart_key in session['cart']:
        del session['cart'][cart_key]
    session.modified = True
    total = get_cart_total(session['cart'])
    return jsonify({'success': True, 'total': total})

# ============ PLACE ORDER ============

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('cart'))
    payment_method = request.form.get('payment_method')
    staff_id = session.get('staff_id', 1)
    total = get_cart_total(session['cart'])
    item_count = get_item_count(session['cart'])
    sale_id = save_order(total, payment_method, staff_id, item_count)
    session['cart'] = {}
    session.modified = True
    return render_template('order_success.html', sale_id=sale_id)

# ============ ORDER HISTORY with MULTI-SEARCH ============

@app.route('/order_history')
def order_history():
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    payment = request.args.get('payment')
    search_date = request.args.get('search_date')
    min_amount = request.args.get('min_amount')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if from_date and to_date:
        from_datetime = from_date.replace('T', ' ') + ':00'
        to_datetime = to_date.replace('T', ' ') + ':59'
        cursor.execute("SELECT * FROM tblSale WHERE SaleDate BETWEEN %s AND %s ORDER BY SaleDate DESC", (from_datetime, to_datetime))
    elif payment:
        cursor.execute("SELECT * FROM tblSale WHERE PaymentMethod = %s ORDER BY SaleDate DESC", (payment,))
    elif search_date:
        cursor.execute("SELECT * FROM tblSale WHERE DATE(SaleDate) = %s ORDER BY SaleDate DESC", (search_date,))
    elif min_amount:
        cursor.execute("SELECT * FROM tblSale WHERE TotalAmount >= %s ORDER BY SaleDate DESC", (int(min_amount),))
    else:
        cursor.execute("SELECT * FROM tblSale ORDER BY SaleDate DESC")
    
    orders = cursor.fetchall()
    conn.close()
    
    return render_template('order_history.html', orders=orders, error=None)

# ============ SEARCH BY SALEID ============

@app.route('/search_order')
def search_order():
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
    order = get_order_by_id(sale_id)
    if order:
        return render_template('order_details.html', order=order)
    return redirect(url_for('order_history'))

# ============ ORDER TYPE (Front-end only) ============

@app.route('/set_order_type', methods=['POST'])
def set_order_type():
    data = request.get_json()
    session['order_type'] = data.get('order_type', 'takeaway')
    session.modified = True
    return jsonify({'success': True})

# ============ RUN THE APP ============

if __name__ == '__main__':
    app.run(debug=True, port=5000)
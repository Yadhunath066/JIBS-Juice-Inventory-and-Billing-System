<<<<<<< HEAD
from flask import Flask, jsonify, request, render_template, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect('menu.db')

# ============ M11: API FOR SANJAYA ============
@app.route('/api/menu_items', methods=['GET'])
def get_menu_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Name, PriceSm, PriceReg, PriceLg, Category, IsVegan FROM tblMenuItem WHERE IsActive = 1")
    rows = cursor.fetchall()
    conn.close()
    
    menu = []
    for row in rows:
        menu.append({
            "name": row[0],
            "sizes": {
                "Sm": row[1],
                "Reg": row[2],
                "Lg": row[3]
            },
            "category": row[4],
            "vegan": bool(row[5])
        })
    
    return jsonify(menu)

@app.route('/')
def home():
    return "Menu API is running! Go to /admin/menu to manage items"

@app.route('/display')
def display_menu():
    return render_template('menu_display.html')

# ============ M4: LIST ALL MENU ITEMS (WITH FILTER) ============
@app.route('/admin/menu')
def list_menu():
    conn = get_db()
    cursor = conn.cursor()
    
    category = request.args.get('category')
    
    if category:
        cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE Category = ?", (category,))
    else:
        cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem")
    
    items = cursor.fetchall()
    conn.close()
    return render_template('menu_list.html', items=items)

# ============ M1: ADD MENU ITEM ============
@app.route('/admin/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        name = request.form['name']
        price_sm = int(float(request.form['price_sm']) * 100)
        price_reg = int(float(request.form['price_reg']) * 100)
        price_lg = int(float(request.form['price_lg']) * 100)
        category = request.form['category']
        is_vegan = 1 if 'is_vegan' in request.form else 0
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (name, price_sm, price_reg, price_lg, category, is_vegan))
        conn.commit()
        conn.close()
        
        return redirect('/admin/menu')
    
    return render_template('menu_add.html')

# ============ M2: EDIT MENU ITEM ============
@app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        price_sm = int(float(request.form['price_sm']) * 100)
        price_reg = int(float(request.form['price_reg']) * 100)
        price_lg = int(float(request.form['price_lg']) * 100)
        category = request.form['category']
        is_vegan = 1 if 'is_vegan' in request.form else 0
        is_active = 1 if 'is_active' in request.form else 0
        
        cursor.execute("""
            UPDATE tblMenuItem 
            SET Name = ?, PriceSm = ?, PriceReg = ?, PriceLg = ?, Category = ?, IsVegan = ?, IsActive = ?
            WHERE ItemID = ?
        """, (name, price_sm, price_reg, price_lg, category, is_vegan, is_active, item_id))
        conn.commit()
        conn.close()
        return redirect('/admin/menu')
    
    cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE ItemID = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    
    return render_template('menu_edit.html', item=item)

# ============ M3: SOFT DELETE MENU ITEM ============
@app.route('/admin/menu/delete/<int:item_id>')
def delete_menu_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblMenuItem SET IsActive = 0 WHERE ItemID = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/menu')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
=======
"""
JIBS Sales Sub-system - Sanjaya
Full menu with categories, sizes, and prices in DKK (øre).
Includes date-time range filter for order history.
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'jibs-secret-key-2026'

# ============ DATABASE SETUP ============
def get_db():
    return sqlite3.connect('jibs.db')

def init_db():
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

init_db()

def get_all_orders():
    """Return all orders, newest first."""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tblSale ORDER BY SaleDate DESC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders

def get_order_by_id(sale_id):
    """Fetch a single order by its SaleID."""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tblSale WHERE SaleID = ?", (sale_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_orders_by_datetime(from_datetime, to_datetime):
    """Return orders whose SaleDate is between the given datetime strings (inclusive)."""
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
    """Insert a new order with current datetime."""
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

# ============ FULL MENU FROM PDF (hardcoded – will be replaced by Monika's API later) ============
menu_data = {
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
    """Helper to get price for a given item name and size."""
    for cat, items in menu_data.items():
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

# ============ ROUTES ============

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/main_menu')
def main_menu():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    return render_template('main_menu.html', staff_name=session.get('staff_name'))

@app.route('/menu')
def menu():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', menu=menu_data)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item_name')
    size = request.form.get('size')
    quantity = int(request.form.get('quantity', 1))
    
    if not size:
        return render_template('menu.html', menu=menu_data, error="Please select a size")
    
    price = find_item_price(item_name, size)
    if not price:
        return redirect(url_for('menu'))
    
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
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'staff_id' not in session:
        return redirect(url_for('login'))
    if 'cart' not in session:
        session['cart'] = {}
    total = get_cart_total(session['cart'])
    return render_template('cart.html', cart=session['cart'], total=total)

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

@app.route('/remove_item/<string:cart_key>', methods=['POST'])
def remove_item(cart_key):
    if cart_key in session['cart']:
        del session['cart'][cart_key]
    session.modified = True
    total = get_cart_total(session['cart'])
    return jsonify({'success': True, 'total': total})

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

@app.route('/order_history')
def order_history():
    # Get filter parameters from URL (date-time range)
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    if from_date and to_date:
        # Convert HTML5 datetime-local format (YYYY-MM-DDTHH:MM) to SQLite format (YYYY-MM-DD HH:MM:SS)
        from_datetime = from_date.replace('T', ' ') + ':00'
        to_datetime = to_date.replace('T', ' ') + ':59'
        orders = get_orders_by_datetime(from_datetime, to_datetime)
    else:
        orders = get_all_orders()
    
    return render_template('order_history.html', orders=orders, error=None)

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

@app.route('/order_details/<int:sale_id>')
def order_details(sale_id):
    order = get_order_by_id(sale_id)
    if order:
        return render_template('order_details.html', order=order)
    return redirect(url_for('order_history'))

@app.route('/set_order_type', methods=['POST'])
def set_order_type():
    data = request.get_json()
    session['order_type'] = data.get('order_type', 'takeaway')
    session.modified = True
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
>>>>>>> 56c3ae5e8d42646d00dae812b056c64e04b3ab22

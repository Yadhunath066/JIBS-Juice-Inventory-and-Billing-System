from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import sqlite3
from functools import wraps

# ============ FIX 1: Added template_folder='.' and static_folder='static' ============
# This tells Flask to look for HTML files in the same folder as app.py
app = Flask(__name__, template_folder='.', static_folder='static')
app.secret_key = 'menu-secret-key-2026'

def get_db():
    return sqlite3.connect('menu.db')

# ============ LOGIN DECORATOR ============
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapper

# ============ LOGIN ROUTES ============
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page - authenticates admin user"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('list_menu'))
        else:
            return render_template('admin_login.html', error="Invalid username or password")
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Clear admin session and redirect to login"""
    session.clear()
    return redirect(url_for('admin_login'))

# ============ M11: API FOR SANJAYA (NO LOGIN REQUIRED) ============
@app.route('/api/menu_items', methods=['GET'])
def get_menu_items():
    """API endpoint for Sanjaya's Sales system - returns all active menu items"""
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
    """Home page - shows API status"""
    return "Menu API is running! Go to /admin/login to manage items"

# ============ CUSTOMER MENU PAGE ============
@app.route('/customer-menu')
def customer_menu():
    """Public customer menu display page"""
    return render_template('customer_menu.html')

# ============ M4: LIST ALL MENU ITEMS (WITH FILTER, SEARCH & VEGAN) ============
@app.route('/admin/menu')
@login_required
def list_menu():
    """Admin menu list page - supports category, search, and vegan filters"""
    conn = get_db()
    cursor = conn.cursor()
    
    category = request.args.get('category')
    search = request.args.get('search')
    vegan = request.args.get('vegan')
    
    if category:
        cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE Category = ?", (category,))
    elif search:
        cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE Name LIKE ?", (f'%{search}%',))
    elif vegan:
        cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE IsVegan = 1")
    else:
        cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem")
    
    items = cursor.fetchall()
    conn.close()
    return render_template('menu_list.html', items=items)

# ============ M1: ADD MENU ITEM ============
@app.route('/admin/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    """Add new menu item - Admin can add juice with sizes and prices"""
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
@login_required
def edit_menu_item(item_id):
    """Edit existing menu item - Update price, name, category, vegan status"""
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
@login_required
def delete_menu_item(item_id):
    """Soft delete - sets IsActive to 0 instead of deleting from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblMenuItem SET IsActive = 0 WHERE ItemID = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/menu')

# ============ FIX 2: Port changed to 5002 ============
if __name__ == '__main__':
    app.run(debug=True, port=5002)
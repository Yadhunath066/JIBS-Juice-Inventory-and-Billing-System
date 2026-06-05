"""
================================================================================
INVENTORY APP - JIBS (Juice Inventory and Billing System) - MYSQL VERSION
Main Flask Application
================================================================================
This is the complete inventory management system with:
- Staff Management (CRUD with GDPR compliance)
- Stock Management (CRUD with validation)
- Recipe Management (Link menu items to ingredients)
- MySQL Database with Views and Triggers
- Stock Check and Stock Deduction APIs for Sanjaya's Sales system
================================================================================
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
app = Flask(__name__)
app.secret_key = 'inventory-secret-key-2026'

# ============================================================================
# LOGIN REQUIRED DECORATOR
# ============================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'staff_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_perishable(value):
    if value is None:
        return False, "Oops! Perishable field is required"
    value_str = str(value).lower()
    if value_str in ['yes', 'no', 'y', 'n', '1', '0', 'true', 'false']:
        return True, ""
    else:
        return False, "Oops! Perishable must be 'Yes' or 'No'."


def validate_category(category):
    valid_categories = ['Fruits', 'Vegetables', 'Dairy', 'Syrups', 'Other']
    if not category:
        return False, "Oops! Category is required"
    if category not in valid_categories:
        return False, f"Oops! '{category}' is not a valid category."
    return True, ""


def validate_quantity(quantity):
    try:
        qty = int(quantity)
        if qty < 0:
            return False, "Oops! Quantity cannot be negative."
        if qty > 999999:
            return False, "Oops! Quantity is too high."
        return True, ""
    except (ValueError, TypeError):
        return False, "Oops! Quantity must be a valid number."


def validate_min_level(min_level):
    try:
        min_lvl = int(min_level)
        if min_lvl < 0:
            return False, "Oops! Minimum stock level cannot be negative."
        if min_lvl > 999999:
            return False, "Oops! Minimum level is too high."
        return True, ""
    except (ValueError, TypeError):
        return False, "Oops! Minimum stock level must be a valid number."


def validate_ingredient_name(name):
    if not name or not name.strip():
        return False, "Oops! Ingredient name cannot be empty."
    if len(name) > 100:
        return False, "Oops! Ingredient name is too long."
    return True, ""


def validate_unit_type(unit):
    valid_units = ['kg', 'g', 'l', 'ml', 'pcs', 'bottle', 'pack', 'box']
    if not unit:
        return False, "Oops! Unit type is required"
    if unit.lower() not in valid_units:
        return False, f"Oops! '{unit}' is not a valid unit."
    return True, ""


# ============================================================================
# DATABASE CONNECTION - MYSQL
# ============================================================================

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="jibs_inventory and staff"
    )


# ============================================================================
# STAFF HELPER FUNCTIONS
# ============================================================================

def get_all_staff():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblStaff ORDER BY StaffID DESC")
    staff = cursor.fetchall()
    conn.close()
    return staff


def get_staff_by_id(staff_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblStaff WHERE StaffID = %s", (staff_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def add_staff(full_name, username, password, role):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO tblStaff (FullName, Username, PasswordHash, Role, IsActive)
        VALUES (%s, %s, %s, %s, %s)
    ''', (full_name, username, password_hash, role, 1))
    conn.commit()
    conn.close()


def update_staff(staff_id, full_name, username, role, is_active, new_password=None):
    conn = get_db()
    cursor = conn.cursor()
    if new_password:
        password_hash = generate_password_hash(new_password)
        cursor.execute('''
            UPDATE tblStaff SET FullName=%s, Username=%s, PasswordHash=%s, Role=%s, IsActive=%s
            WHERE StaffID=%s
        ''', (full_name, username, password_hash, role, is_active, staff_id))
    else:
        cursor.execute('''
            UPDATE tblStaff SET FullName=%s, Username=%s, Role=%s, IsActive=%s
            WHERE StaffID=%s
        ''', (full_name, username, role, is_active, staff_id))
    conn.commit()
    conn.close()


def delete_staff(staff_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tblStaff 
        SET FullName='[ANONYMIZED]', Username='deleted_user', IsActive=0
        WHERE StaffID=%s
    ''', (staff_id,))
    conn.commit()
    conn.close()


# ============================================================================
# STOCK HELPER FUNCTIONS
# ============================================================================

def get_all_stock():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblStock ORDER BY IngredientName")
    stock = cursor.fetchall()
    conn.close()
    return stock


def get_stock_by_id(stock_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblStock WHERE StockID = %s", (stock_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def add_stock(name, quantity, min_level, unit, perishable, category='Other'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tblStock (IngredientName, Category, QuantityInStock, MinStockLevel, UnitType, IsPerishable)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (name, category, quantity, min_level, unit, perishable))
    conn.commit()
    conn.close()


def update_stock(stock_id, name, quantity, min_level, unit, perishable, category='Other'):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tblStock SET IngredientName=%s, Category=%s, QuantityInStock=%s, MinStockLevel=%s, UnitType=%s, IsPerishable=%s
        WHERE StockID=%s
    ''', (name, category, quantity, min_level, unit, perishable, stock_id))
    conn.commit()
    conn.close()


def delete_stock(stock_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblStock WHERE StockID=%s", (stock_id,))
    conn.commit()
    conn.close()


def get_low_stock():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vw_LowStock")
    items = cursor.fetchall()
    conn.close()
    return items


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tblStaff WHERE Username = %s AND IsActive = 1", (username,))
        staff = cursor.fetchone()
        conn.close()
        
        if staff and check_password_hash(staff['PasswordHash'], password):
            session['staff_id'] = staff['StaffID']
            session['staff_name'] = staff['FullName']
            session['staff_role'] = staff['Role']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ============================================================================
# DASHBOARD ROUTE
# ============================================================================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tblStaff WHERE IsActive = 1")
    staff_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tblStock")
    stock_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tblStock WHERE QuantityInStock < MinStockLevel")
    low_stock_count = cursor.fetchone()[0]
    conn.close()
    
    return render_template('dashboard.html', 
                          staff_count=staff_count, 
                          stock_count=stock_count, 
                          low_stock_count=low_stock_count,
                          staff_name=session.get('staff_name'),
                          staff_role=session.get('staff_role'))


# ============================================================================
# STAFF MANAGEMENT ROUTES
# ============================================================================

@app.route('/staff')
@login_required
def staff_list():
    if session.get('staff_role') != 'Admin':
        return "Access Denied. Admin only.", 403
    staff = get_all_staff()
    return render_template('staff_list.html', staff_list=staff, staff_name=session.get('staff_name'), staff_role=session.get('staff_role'))


@app.route('/staff/add', methods=['GET', 'POST'])
@login_required
def staff_add():
    if session.get('staff_role') != 'Admin':
        return "Access Denied. Admin only.", 403
    
    error = None
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not full_name or not username or not password or not role:
            error = "All fields are required"
        else:
            try:
                add_staff(full_name, username, password, role)
                return redirect(url_for('staff_list'))
            except mysql.connector.IntegrityError:
                error = "Username already exists!"
    
    return render_template('staff_add.html', 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'),
                          error=error)


@app.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def staff_edit(staff_id):
    if session.get('staff_role') != 'Admin':
        return "Access Denied. Admin only.", 403
    
    staff = get_staff_by_id(staff_id)
    if not staff:
        return "Staff not found", 404
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        is_active = 1 if request.form.get('is_active') == '1' else 0
        
        update_staff(staff_id, full_name, username, role, is_active, password if password else None)
        return redirect(url_for('staff_list'))
    
    return render_template('staff_edit.html', staff=staff, 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'))


@app.route('/staff/delete/<int:staff_id>')
@login_required
def staff_delete(staff_id):
    if session.get('staff_role') != 'Admin':
        return "Access Denied. Admin only.", 403
    
    delete_staff(staff_id)
    return redirect(url_for('staff_list'))


@app.route('/staff/filter/<role>')
@login_required
def filter_staff_by_role(role):
    if session.get('staff_role') != 'Admin':
        return "Access Denied. Admin only.", 403
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblStaff WHERE Role = %s ORDER BY StaffID", (role,))
    staff = cursor.fetchall()
    conn.close()
    
    return render_template('staff_list.html', staff_list=staff, 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'),
                          filter_role=role)


@app.route('/staff/search')
@login_required
def search_staff():
    if session.get('staff_role') != 'Admin':
        return "Access Denied. Admin only.", 403
    
    search_term = request.args.get('name', '')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblStaff WHERE FullName LIKE %s ORDER BY StaffID", (f'%{search_term}%',))
    staff = cursor.fetchall()
    conn.close()
    
    return render_template('staff_list.html', staff_list=staff, 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'),
                          search_term=search_term)


# ============================================================================
# STOCK MANAGEMENT ROUTES
# ============================================================================

@app.route('/stock')
@login_required
def stock_list():
    stock = get_all_stock()
    return render_template('stock_list.html', stock=stock, 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'))


@app.route('/stock/add', methods=['GET', 'POST'])
@login_required
def stock_add():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        quantity_str = request.form.get('quantity')
        min_level_str = request.form.get('min_level')
        unit = request.form.get('unit')
        perishable = 1 if request.form.get('perishable') else 0
        category = request.form.get('category', 'Other')
        
        valid = True
        error_messages = []
        
        name_valid, name_msg = validate_ingredient_name(name)
        if not name_valid:
            error_messages.append(name_msg)
            valid = False
        
        quantity_valid, quantity_msg = validate_quantity(quantity_str)
        if not quantity_valid:
            error_messages.append(quantity_msg)
            valid = False
        
        min_level_valid, min_level_msg = validate_min_level(min_level_str)
        if not min_level_valid:
            error_messages.append(min_level_msg)
            valid = False
        
        unit_valid, unit_msg = validate_unit_type(unit)
        if not unit_valid:
            error_messages.append(unit_msg)
            valid = False
        
        category_valid, category_msg = validate_category(category)
        if not category_valid:
            error_messages.append(category_msg)
            valid = False
        
        if not valid:
            error = "\n".join(error_messages)
        else:
            quantity = int(quantity_str)
            min_level = int(min_level_str)
            try:
                add_stock(name, quantity, min_level, unit, perishable, category)
                return redirect(url_for('stock_list'))
            except mysql.connector.IntegrityError:
                error = "Oops! An ingredient with this name already exists."
    
    return render_template('stock_add.html', 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'),
                          error=error)


@app.route('/stock/edit/<int:stock_id>', methods=['GET', 'POST'])
@login_required
def stock_edit(stock_id):
    stock = get_stock_by_id(stock_id)
    if not stock:
        return "Ingredient not found", 404
    
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        quantity_str = request.form.get('quantity')
        min_level_str = request.form.get('min_level')
        unit = request.form.get('unit')
        perishable = 1 if request.form.get('perishable') else 0
        category = request.form.get('category', 'Other')
        
        valid = True
        error_messages = []
        
        name_valid, name_msg = validate_ingredient_name(name)
        if not name_valid:
            error_messages.append(name_msg)
            valid = False
        
        quantity_valid, quantity_msg = validate_quantity(quantity_str)
        if not quantity_valid:
            error_messages.append(quantity_msg)
            valid = False
        
        min_level_valid, min_level_msg = validate_min_level(min_level_str)
        if not min_level_valid:
            error_messages.append(min_level_msg)
            valid = False
        
        unit_valid, unit_msg = validate_unit_type(unit)
        if not unit_valid:
            error_messages.append(unit_msg)
            valid = False
        
        category_valid, category_msg = validate_category(category)
        if not category_valid:
            error_messages.append(category_msg)
            valid = False
        
        if not valid:
            error = "\n".join(error_messages)
        else:
            quantity = int(quantity_str)
            min_level = int(min_level_str)
            update_stock(stock_id, name, quantity, min_level, unit, perishable, category)
            return redirect(url_for('stock_list'))
    
    return render_template('stock_edit.html', stock=stock, 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'),
                          error=error)


@app.route('/stock/delete/<int:stock_id>')
@login_required
def stock_delete(stock_id):
    delete_stock(stock_id)
    return redirect(url_for('stock_list'))


@app.route('/low_stock')
@login_required
def low_stock():
    items = get_low_stock()
    return render_template('low_stock.html', items=items, 
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'))


# ============================================================================
# QUICK UPDATE STOCK (AJAX)
# ============================================================================

@app.route('/stock/quick-update/<int:stock_id>', methods=['POST'])
@login_required
def quick_update_stock(stock_id):
    data = request.get_json()
    new_quantity = data.get('quantity')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblStock SET QuantityInStock = %s WHERE StockID = %s", (new_quantity, stock_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


# ============================================================================
# GET BY ID API ENDPOINTS (AJAX)
# ============================================================================

@app.route('/stock/get/<int:stock_id>')
@login_required
def get_stock_by_id_api(stock_id):
    stock = get_stock_by_id(stock_id)
    return jsonify(stock)


@app.route('/staff/get/<int:staff_id>')
@login_required
def get_staff_by_id_api(staff_id):
    staff = get_staff_by_id(staff_id)
    return jsonify(staff)


# ============================================================================
# API FOR DASHBOARD STOCK HEALTH
# ============================================================================

@app.route('/api/stock-health')
@login_required
def api_stock_health():
    stock = get_all_stock()
    result = []
    for item in stock:
        result.append({
            'IngredientName': item['IngredientName'],
            'QuantityInStock': item['QuantityInStock'],
            'MinStockLevel': item['MinStockLevel'],
            'UnitType': item['UnitType']
        })
    return jsonify(result)


# ============================================================================
# STOCK CHECK AND DEDUCTION APIS FOR SANJAYA (No login required)
# ============================================================================

@app.route('/api/check_stock', methods=['POST'])
def check_stock():
    """API for Sanjaya to check if enough stock is available"""
    data = request.get_json()
    items = data.get('items', [])
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    for item in items:
        item_name = item.get('name')
        quantity = item.get('quantity', 0)
        
        cursor.execute("SELECT QuantityInStock FROM tblStock WHERE IngredientName = %s", (item_name,))
        result = cursor.fetchone()
        if not result or result['QuantityInStock'] < quantity:
            conn.close()
            return jsonify({
                'available': False,
                'message': f'Insufficient stock for {item_name}'
            })
    
    conn.close()
    return jsonify({'available': True, 'message': 'All items in stock'})


@app.route('/api/deduct_stock', methods=['POST'])
def deduct_stock():
    """API for Sanjaya to deduct stock after order is placed"""
    data = request.get_json()
    items = data.get('items', [])
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        for item in items:
            item_name = item.get('name')
            quantity = item.get('quantity', 0)
            cursor.execute("UPDATE tblStock SET QuantityInStock = QuantityInStock - %s WHERE IngredientName = %s", (quantity, item_name))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Stock deducted successfully'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)})


# ============================================================================
# RECIPE MANAGEMENT ROUTES
# ============================================================================

@app.route('/recipe')
@login_required
def recipe_list():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.RecipeID, r.ItemID, r.StockID, r.QuantityUsed, s.IngredientName
        FROM tblRecipe r
        JOIN tblStock s ON r.StockID = s.StockID
    ''')
    recipes = cursor.fetchall()
    conn.close()
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT StockID, IngredientName, UnitType FROM tblStock ORDER BY IngredientName")
    stock_items = cursor.fetchall()
    conn.close()
    
    return render_template('recipe_list.html', recipes=recipes, stock_items=stock_items,
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'))


@app.route('/recipe/add', methods=['GET', 'POST'])
@login_required
def recipe_add():
    if request.method == 'POST':
        item_id = int(request.form.get('item_id'))
        stock_id = int(request.form.get('stock_id'))
        quantity_used = int(request.form.get('quantity_used'))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tblRecipe (ItemID, StockID, QuantityUsed)
            VALUES (%s, %s, %s)
        ''', (item_id, stock_id, quantity_used))
        conn.commit()
        conn.close()
        return redirect(url_for('recipe_list'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT StockID, IngredientName FROM tblStock ORDER BY IngredientName")
    stock_items = cursor.fetchall()
    conn.close()
    
    return render_template('recipe_add.html', stock_items=stock_items,
                          staff_name=session.get('staff_name'), 
                          staff_role=session.get('staff_role'))


@app.route('/recipe/get/<int:recipe_id>')
@login_required
def get_recipe_by_id(recipe_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.RecipeID, r.ItemID, r.StockID, r.QuantityUsed, s.IngredientName, s.UnitType
        FROM tblRecipe r
        JOIN tblStock s ON r.StockID = s.StockID
        WHERE r.RecipeID = %s
    ''', (recipe_id,))
    recipe_data = cursor.fetchall()
    conn.close()
    
    ingredients = []
    for r in recipe_data:
        ingredients.append({
            'id': r['StockID'],
            'name': r['IngredientName'],
            'unit': r['UnitType'],
            'quantity': r['QuantityUsed'],
            'pricePerUnit': 10,
            'totalCost': 10 * r['QuantityUsed']
        })
    
    return jsonify({
        'name': f'Recipe {recipe_id}',
        'menuItemId': recipe_data[0]['ItemID'] if recipe_data else '',
        'ingredients': ingredients,
        'instructions': '',
        'sellingPrice': 0
    })


@app.route('/recipe/save', methods=['POST'])
@login_required
def save_recipe_api():
    data = request.get_json()
    return jsonify({'success': True, 'recipe_id': data.get('recipeId', 'new')})


# ============================================================================
# FORGOT PASSWORD & CONTACT ROUTES
# ============================================================================

@app.route('/forgot-password')
def forgot_password():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forgot Password - JIBS</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: #060d0a;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .message-card {
                background: rgba(15, 26, 22, 0.6);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
                padding: 40px;
                text-align: center;
                max-width: 400px;
            }
            h1 { color: #f8fafc; margin-bottom: 15px; }
            p { color: #94a3b8; margin-bottom: 25px; }
            .btn {
                background: #22c55e;
                color: white;
                padding: 10px 24px;
                text-decoration: none;
                border-radius: 12px;
                display: inline-block;
            }
            .btn:hover { background: #16a34a; }
        </style>
    </head>
    <body>
        <div class="message-card">
            <h1>Forgot Password</h1>
            <p>Please contact your system administrator to reset your password.</p>
            <a href="/login" class="btn">Back to Login</a>
        </div>
    </body>
    </html>
    '''


@app.route('/contact')
def contact():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Contact Admin - JIBS</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: #060d0a;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .message-card {
                background: rgba(15, 26, 22, 0.6);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
                padding: 40px;
                text-align: center;
                max-width: 400px;
            }
            h1 { color: #f8fafc; margin-bottom: 15px; }
            p { color: #94a3b8; margin-bottom: 10px; }
            .email {
                color: #22c55e;
                font-size: 18px;
                margin: 20px 0;
            }
            .btn {
                background: #22c55e;
                color: white;
                padding: 10px 24px;
                text-decoration: none;
                border-radius: 12px;
                display: inline-block;
            }
            .btn:hover { background: #16a34a; }
        </style>
    </head>
    <body>
        <div class="message-card">
            <h1>Contact Admin</h1>
            <p>For any assistance, please email:</p>
            <div class="email">admin@sipandgo.com</div>
            <a href="/login" class="btn">Back to Login</a>
        </div>
    </body>
    </html>
    '''


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5001)
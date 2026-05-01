from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect('menu.db')

@app.route('/api/menu_items', methods=['GET'])
def get_menu_items():
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT Name, PriceSm, PriceReg, PriceLg, Category, IsVegan FROM tblMenuItem WHERE IsActive = 1"
    params = []
    
    category = request.args.get('category')
    vegan = request.args.get('vegan')
    
    if category:
        query += " AND Category = ?"
        params.append(category)
    
    if vegan == 'true':
        query += " AND IsVegan = 1"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for row in rows:
        items.append({
            "name": row[0],
            "prices": {
                "Sm": row[1],
                "Reg": row[2],
                "Lg": row[3]
            },
            "category": row[4],
            "isVegan": bool(row[5])
        })
    
    return jsonify(items)

@app.route('/api/menu_items/<int:item_id>', methods=['PUT'])
def edit_menu_item(item_id):
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tblMenuItem 
        SET Name=?, PriceSm=?, PriceReg=?, PriceLg=?, Category=?, IsVegan=?
        WHERE ItemID=?
    ''', (data['name'], data['priceSm'], data['priceReg'], data['priceLg'], data['category'], data['isVegan'], item_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item updated"})

@app.route('/api/menu_items/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tblMenuItem SET IsActive = 0 WHERE ItemID = ?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item deactivated"})

@app.route('/')
def home():
    return "Menu API is running!"

if __name__ == '__main__':
    app.run(debug=True, port=5002)
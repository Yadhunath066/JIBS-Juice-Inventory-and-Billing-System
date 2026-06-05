# stored_procedures.py - Stored procedure equivalents for Menu Management system
# Since SQLite does not support traditional stored procedures,
# these Python functions act as stored procedures for the database operations

import sqlite3

# ============ STORED PROCEDURE 1: SP_AddMenuItem ============
# Purpose: Add a new menu item to the database
# Parameters: name, price_sm, price_reg, price_lg, category, is_vegan
def SP_AddMenuItem(name, price_sm, price_reg, price_lg, category, is_vegan):
    """
    Stored procedure to insert a new menu item into tblMenuItem.
    Returns the new ItemID if successful, None if failed.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO tblMenuItem (Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (name, price_sm, price_reg, price_lg, category, is_vegan))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id
    except Exception as e:
        conn.close()
        print(f"Error adding menu item: {e}")
        return None


# ============ STORED PROCEDURE 2: SP_UpdateMenuItem ============
# Purpose: Update an existing menu item
# Parameters: item_id, name, price_sm, price_reg, price_lg, category, is_vegan, is_active
def SP_UpdateMenuItem(item_id, name, price_sm, price_reg, price_lg, category, is_vegan, is_active):
    """
    Stored procedure to update an existing menu item in tblMenuItem.
    Returns True if successful, False if failed.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE tblMenuItem 
            SET Name = ?, PriceSm = ?, PriceReg = ?, PriceLg = ?, Category = ?, IsVegan = ?, IsActive = ?
            WHERE ItemID = ?
        ''', (name, price_sm, price_reg, price_lg, category, is_vegan, is_active, item_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Error updating menu item: {e}")
        return False


# ============ STORED PROCEDURE 3: SP_DeleteMenuItem (Soft Delete) ============
# Purpose: Soft delete a menu item (set IsActive = 0)
# Parameters: item_id
def SP_DeleteMenuItem(item_id):
    """
    Stored procedure to soft delete a menu item (sets IsActive = 0).
    Returns True if successful, False if failed.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tblMenuItem SET IsActive = 0 WHERE ItemID = ?", (item_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Error deleting menu item: {e}")
        return False


# ============ STORED PROCEDURE 4: SP_GetAllMenuItems ============
# Purpose: Get all active menu items
# Returns: List of all active menu items
def SP_GetAllMenuItems():
    """
    Stored procedure to retrieve all active menu items from tblMenuItem.
    Returns a list of tuples containing menu item data.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE IsActive = 1")
    items = cursor.fetchall()
    conn.close()
    return items


# ============ STORED PROCEDURE 5: SP_GetMenuItemById ============
# Purpose: Get a specific menu item by ID
# Parameters: item_id
# Returns: Single menu item tuple or None
def SP_GetMenuItemById(item_id):
    """
    Stored procedure to retrieve a specific menu item by its ItemID.
    Returns a tuple of menu item data or None if not found.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE ItemID = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item


# ============ STORED PROCEDURE 6: SP_GetMenuItemsByCategory ============
# Purpose: Get menu items filtered by category
# Parameters: category
# Returns: List of menu items in the specified category
def SP_GetMenuItemsByCategory(category):
    """
    Stored procedure to retrieve menu items filtered by category.
    Returns a list of tuples matching the category.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE Category = ? AND IsActive = 1", (category,))
    items = cursor.fetchall()
    conn.close()
    return items


# ============ STORED PROCEDURE 7: SP_SearchMenuItemsByName ============
# Purpose: Search menu items by name (partial match)
# Parameters: search_term
# Returns: List of menu items matching the search term
def SP_SearchMenuItemsByName(search_term):
    """
    Stored procedure to search for menu items by name (partial match).
    Returns a list of tuples matching the search term.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE Name LIKE ? AND IsActive = 1", (f'%{search_term}%',))
    items = cursor.fetchall()
    conn.close()
    return items


# ============ STORED PROCEDURE 8: SP_GetVeganMenuItems ============
# Purpose: Get all vegan menu items
# Returns: List of vegan menu items
def SP_GetVeganMenuItems():
    """
    Stored procedure to retrieve all vegan menu items (IsVegan = 1).
    Returns a list of tuples for vegan items.
    """
    conn = sqlite3.connect('menu.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ItemID, Name, PriceSm, PriceReg, PriceLg, Category, IsVegan, IsActive FROM tblMenuItem WHERE IsVegan = 1 AND IsActive = 1")
    items = cursor.fetchall()
    conn.close()
    return items


# ============ TEST THE STORED PROCEDURES ============
if __name__ == '__main__':
    print("=== Testing Stored Procedures ===\n")
    
    # Test SP_GetAllMenuItems
    print("1. SP_GetAllMenuItems - All active menu items:")
    items = SP_GetAllMenuItems()
    for item in items[:3]:  # Show first 3 only
        print(f"   {item[1]} - {item[2]/100} kr")
    print(f"   ... Total {len(items)} items\n")
    
    # Test SP_GetMenuItemById
    print("2. SP_GetMenuItemById (ID=1):")
    item = SP_GetMenuItemById(1)
    if item:
        print(f"   Found: {item[1]}\n")
    
    # Test SP_GetVeganMenuItems
    print("3. SP_GetVeganMenuItems:")
    vegan_items = SP_GetVeganMenuItems()
    print(f"   Found {len(vegan_items)} vegan items\n")
    
    print("=== All stored procedures working correctly ===")
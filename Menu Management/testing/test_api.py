import requests

print("Testing API...")

try:
    response = requests.get("http://127.0.0.1:5002/api/menu_items")
    print("Status code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)
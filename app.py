from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql

app = Flask(__name__)

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})



# Function to get a MySQL connection
def get_db_connection():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='venkat123',
            database='naatha',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as e:
        print("MySQL connection error:", e)
        return None
    


# API: get menu items
@app.route('/api/menu')
def menu():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM menu_items WHERE availability=1")
            menu_items = cursor.fetchall()
    finally:
        conn.close()
    return jsonify(menu_items)

# API: login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error":"Database connection failed"}),500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s AND password_hash=%s", (email,password))
            user = cursor.fetchone()
    finally:
        conn.close()
    if user:
        return jsonify({"status":"success", "user_id": user['user_id']})
    else:
        return jsonify({"status":"fail"}), 401

# API: register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error":"Database connection failed"}),500
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name,email,phone,password_hash) VALUES (%s,%s,%s,%s)",
                (name,email,phone,password)
            )
            conn.commit()
            return jsonify({"status":"success"})
    except pymysql.err.IntegrityError:
        return jsonify({"status":"fail", "message":"Email already exists"}), 400
    finally:
        conn.close()
        

@app.route('/api/place_order', methods=['POST'])
def place_order():
    data = request.json
    user_email = data.get('email')
    name = data.get('name')
    address = data.get('address')
    phone = data.get('phone')
    cart = data.get('cart', [])

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # Find user_id from email
            cursor.execute("SELECT user_id FROM users WHERE email=%s", (user_email,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"error": "User not found"}), 404

            user_id = user['user_id']
            total = sum(float(item['price']) * int(item['qty']) for item in cart)

            # Insert order
            cursor.execute(
                "INSERT INTO orders (user_id, name, address, phone, total_price, status) VALUES (%s,%s,%s,%s,%s,%s)",
                (user_id, name, address, phone, total, 'Placed')
            )
            order_id = cursor.lastrowid

            # Insert order items
            for item in cart:
                cursor.execute(
                    "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s,%s,%s,%s)",
                    (order_id, item['item_id'], int(item['qty']), float(item['price']))
                )

            conn.commit()
        return jsonify({"status": "success", "order_id": order_id})
    finally:
        conn.close()


@app.route('/api/orders/<email>', methods=['GET'])
def get_orders(email):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            if not user:
                return jsonify([])

            cursor.execute("SELECT * FROM orders WHERE user_id=%s ORDER BY order_id DESC", (user['user_id'],))
            orders = cursor.fetchall()
        return jsonify(orders)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

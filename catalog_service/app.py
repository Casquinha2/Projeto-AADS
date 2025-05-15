from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json
app = Flask(__name__)

DB_CONFIG = {
    "dbname": "orders_db",
    "user": "user",
    "password": "password",
    "host": "postgres_orders",
    "port": 5432,
}

def initialize_database():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        product_details JSON NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Tabela 'orders' inicializada com sucesso.")
    except Exception as e: 
        print(f"Erro ao inicializar a tabela: {e}")

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    if not data or not data.get('user_id') or not data.get('product_details'):
        return jsonify({"error": "Invalid input"}), 400

    user_id = data['user_id']

    try:
        user_service_url = f"http://user_service:6000/users/{user_id}"
        response = requests.get(user_service_url)
        if response.status_code != 200:
            return jsonify({"error": "User does not exist"}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error contacting User Service: {str(e)}"}), 500

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        product_details_json = json.dumps(data['product_details'])
        cursor.execute(
            "INSERT INTO orders (user_id, product_details) VALUES (%s, %s) RETURNING id;",
            (user_id, product_details_json)
        )
        order_id = cursor.fetchone()[0]
        conn.commit()

        return jsonify({"id": order_id, "user_id": user_id, "product_details": data['product_details']}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()



@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM orders;")
        orders = cursor.fetchall()

        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM orders WHERE id = %s;", (order_id,))
        order = cursor.fetchone()

        if order:
            return jsonify(order), 200
        return jsonify({"error": "Order not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)

#docker exec -it postgres_orders psql -U user -d order_db
from flask import Blueprint, request, jsonify
from model import Order
import requests

order_blueprint = Blueprint('order', __name__)

orders = {}  

def verificar_utilizador(user_id):
    
    try:
        response = requests.get(f'http://user_service:6000/users/{user_id}')
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print("Erro ao conectar ao User Service:", e)
        return False

@order_blueprint.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order.to_dict())
    return jsonify({'error': 'Order not found'}), 404

@order_blueprint.route('/', methods=['POST'])
def create_order():
    order_data = request.json
    order = Order(order_id=order_data['order_id'], user_id=order_data['user_id'], product_details=order_data['product_details'])
    orders[order.order_id] = order
    return jsonify(order.to_dict()), 201
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CLIENT_API_URL = 'http://localhost:8002/clientes/'
SHIPMENT_API_URL = 'http://localhost:8001/estado_envio/'

@app.route('/generar_boleta/', methods=['POST'])
def generate_receipt():
    data = request.get_json()
    if not data or not data.get('items'):
        return jsonify({"error": "La compra debe poseer al menos 1 articulo"}), 400

    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({"error": "El customer_id es obligatorio"}), 400

    try:
        total = sum(item['precio'] * item['cantidad'] for item in data['items'])
    except KeyError:
        return jsonify({"error": "Cada artículo debe tener 'precio' y 'cantidad'"}), 400
    except TypeError:
        return jsonify({"error": "El 'precio' y 'cantidad' deben ser números"}), 400

    receipt = {
        "customer_id": customer_id,
        "items": data['items'],
        "total": total
    }

    try:
        client_response = requests.post(CLIENT_API_URL, json={"customer_id": customer_id})
        client_response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Error al comunicarse con el API de clientes: {str(e)}"}), 500

    order_id = data.get('order_id')
    if not order_id:
        return jsonify({"error": "El order_id es obligatorio"}), 400

    try:
        shipment_response = requests.post(SHIPMENT_API_URL, json={"order_id": order_id, "status": "En proceso"})
        shipment_response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Error al comunicarse con el API de logística: {str(e)}"}), 500

    return jsonify(receipt), 200

@app.route('/estado', methods=['GET'])
def status():
    return jsonify({"estado": "API de ventas está funcionando"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

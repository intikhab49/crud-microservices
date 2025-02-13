from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# In-memory storage
users = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    user = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'email': data['email'],
        'created_at': datetime.now().isoformat()
    }
    users.append(user)
    return jsonify(user), 201

@app.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    for user in users:
        if user['id'] == user_id:
            user['name'] = data['name']
            user['email'] = data['email']
            return jsonify(user)
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    for i, user in enumerate(users):
        if user['id'] == user_id:
            del users[i]
            return '', 204
    
    return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

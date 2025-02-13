from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import logging
import os
from models import User

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB configuration
app.config['MONGO_URI'] = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/user_management')
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = list(mongo.db.users.find())
        return jsonify([User.from_db_document(user).to_dict() for user in users])
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database connection error'}), 500

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400

    try:
        existing_user = mongo.db.users.find_one({'email': data['email']})
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        user = User(name=data['name'], email=data['email'])
        result = mongo.db.users.insert_one(user.to_document())
        user._id = result.inserted_id
        return jsonify(user.to_dict()), 201
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400

    try:
        user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user_doc:
            return jsonify({'error': 'User not found'}), 404

        existing_user = mongo.db.users.find_one({
            'email': data['email'],
            '_id': {'$ne': ObjectId(user_id)}
        })
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        update_result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'name': data['name'],
                'email': data['email']
            }}
        )

        if update_result.modified_count:
            updated_user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return jsonify(User.from_db_document(updated_user).to_dict())
        return jsonify({'error': 'No changes made'}), 400
    except Exception as e:
        logging.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = mongo.db.users.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count:
            return '', 204
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import models after db initialization to avoid circular imports
from models import User

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logging.error(f"Database error in get_users: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Name and email are required'}), 400

        # Validate input data
        if not isinstance(data['name'], str) or not isinstance(data['email'], str):
            return jsonify({'error': 'Invalid data types. Name and email must be strings'}), 400

        if len(data['name'].strip()) == 0 or len(data['email'].strip()) == 0:
            return jsonify({'error': 'Name and email cannot be empty'}), 400

        existing_user = User.query.filter_by(email=data['email'].strip()).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        user = User(name=data['name'].strip(), email=data['email'].strip())
        db.session.add(user)
        db.session.commit()

        logging.info(f"Successfully created user with ID: {user.id}")
        return jsonify(user.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Name and email are required'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        existing_user = User.query.filter(
            User.email == data['email'].strip(),
            User.id != user_id
        ).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        user.name = data['name'].strip()
        user.email = data['email'].strip()
        db.session.commit()

        return jsonify(user.to_dict())

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
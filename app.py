from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import os
import logging

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logging.basicConfig(level=logging.DEBUG)

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

def wait_for_database():
    import time
    from sqlalchemy import create_engine
    from sqlalchemy.exc import OperationalError
    retries = 15
    delay = 5
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    for i in range(retries):
        try:
            connection = engine.connect()
            connection.close()
            return True
        except OperationalError:
            print(f"Waiting for database... (attempt {i+1}/{retries})")
            time.sleep(delay)
    return False

def initialize_database():
    try:
        with app.app_context():
            result = db.session.execute(text("SELECT current_database();"))
            current_db = result.scalar()
            print(f"Connected to database: {current_db}")
            inspector = inspect(db.engine)
            if not inspector.has_table('users'):
                db.create_all()
                print("Created database tables")
            else:
                print("Tables already exist")
    except Exception as e:
        print(f"Database initialization failed: {str(e)}")
        raise

@app.route('/')
def index():
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('index.html', users=users)
    except Exception as e:
        print(f"Failed to fetch users: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500

@app.route('/users', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"id": new_user.id, "name": new_user.name, "email": new_user.email, "created_at": new_user.created_at.isoformat()}), 201
    except Exception as e:
        logging.error(f"User creation failed: {str(e)}")
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([{"id": u.id, "name": u.name, "email": u.email, "created_at": u.created_at.isoformat()} for u in users])
    except Exception as e:
        print(f"Failed to fetch users: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        db.session.commit()
        return jsonify({"id": user.id, "name": user.name, "email": user.email, "created_at": user.created_at.isoformat()})
    except Exception as e:
        logging.error(f"User update failed: {str(e)}")
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User {user_id} deleted"}), 200
    except Exception as e:
        logging.error(f"User deletion failed: {str(e)}")
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    if wait_for_database():
        initialize_database()
        app.run(host='0.0.0.0', port=5000)
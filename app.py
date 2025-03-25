from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from prometheus_client import Counter, generate_latest, REGISTRY
import os
import logging
import requests
from datetime import datetime

app = Flask(__name__)

# Flask configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logging.basicConfig(level=logging.DEBUG)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Prometheus metrics
REQUESTS = Counter('requests_total', 'Total HTTP Requests', ['method', 'endpoint'])

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Wait for database to be ready
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

# Initialize database and tables
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

# Helper function to log actions to the logging service
def log_action(event, user_id=None, details=None):
    try:
        payload = {
            "event": event,
            "user_id": user_id,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        requests.post("http://logging-service:5001/logs", json=payload, timeout=2)
    except requests.RequestException as e:
        logging.error(f"Failed to send log to logging service: {str(e)}")

# Run initialization on startup
if wait_for_database():
    initialize_database()

# Routes
@app.route('/')
def index():
    REQUESTS.labels(method='GET', endpoint='/').inc()
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template('index.html', users=users)
    except Exception as e:
        print(f"Failed to fetch users: {str(e)}")
        log_action("fetch_users_failed", details={"error": str(e)})
        return jsonify({"error": "Database operation failed"}), 500

@app.route('/users', methods=['POST'])
def add_user():
    REQUESTS.labels(method='POST', endpoint='/users').inc()
    try:
        data = request.get_json()
        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        log_action("user_added", new_user.id, {"name": new_user.name, "email": new_user.email})
        return jsonify({
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "created_at": new_user.created_at.isoformat()
        }), 201
    except Exception as e:
        logging.error(f"User creation failed: {str(e)}")
        log_action("user_add_failed", details={"error": str(e), "data": data})
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    REQUESTS.labels(method='GET', endpoint='/users').inc()
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        log_action("users_fetched", details={"count": len(users)})
        return jsonify([{
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "created_at": u.created_at.isoformat()
        } for u in users])
    except Exception as e:
        print(f"Failed to fetch users: {str(e)}")
        log_action("fetch_users_failed", details={"error": str(e)})
        return jsonify({"error": "Database operation failed"}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    REQUESTS.labels(method='PUT', endpoint='/users/<id>').inc()
    try:
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        old_name, old_email = user.name, user.email
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        db.session.commit()
        log_action("user_updated", user_id, {
            "old": {"name": old_name, "email": old_email},
            "new": {"name": user.name, "email": user.email}
        })
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        })
    except Exception as e:
        logging.error(f"User update failed: {str(e)}")
        log_action("user_update_failed", user_id, {"error": str(e), "data": data})
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    REQUESTS.labels(method='DELETE', endpoint='/users/<id>').inc()
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        log_action("user_deleted", user_id, {"name": user.name, "email": user.email})
        return jsonify({"message": f"User {user_id} deleted"}), 200
    except Exception as e:
        logging.error(f"User deletion failed: {str(e)}")
        log_action("user_delete_failed", user_id, {"error": str(e)})
        return jsonify({"error": "Database operation failed", "details": str(e)}), 500

@app.route('/health')
def health():
    REQUESTS.labels(method='GET', endpoint='/health').inc()
    return jsonify({"status": "healthy"}), 200

@app.route('/metrics')
def metrics():
    REQUESTS.labels(method='GET', endpoint='/metrics').inc()
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain; version=0.0.4'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
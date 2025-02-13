from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func

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

@app.route('/dashboard')
def dashboard():
    try:
        # Calculate statistics
        stats = {
            'total_users': User.query.count(),
            'new_users_today': User.query.filter(
                User.created_at >= datetime.utcnow().date()
            ).count(),
            'top_domain': get_top_email_domain()
        }

        # Get recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

        # Get registration trend data
        chart_data = get_registration_trend()

        return render_template('dashboard.html',
                             stats=stats,
                             recent_users=recent_users,
                             chart_data=chart_data)
    except Exception as e:
        logging.error(f"Error in dashboard route: {str(e)}")
        return jsonify({'error': 'Error loading dashboard'}), 500

def get_top_email_domain():
    try:
        users = User.query.all()
        domains = [user.email.split('@')[1] for user in users]
        if not domains:
            return "N/A"
        return Counter(domains).most_common(1)[0][0]
    except Exception:
        return "N/A"

def get_registration_trend():
    try:
        # Get the last 7 days of registration data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=6)

        # Query daily registration counts
        daily_counts = db.session.query(
            func.date(User.created_at).label('date'),
            func.count().label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.date(User.created_at)
        ).all()

        # Convert to dict for easy lookup
        counts_dict = {str(date): count for date, count in daily_counts}

        # Generate labels and values for all days
        labels = []
        values = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            labels.append(date_str)
            values.append(counts_dict.get(date_str, 0))
            current_date += timedelta(days=1)

        return {
            'labels': labels,
            'values': values
        }
    except Exception as e:
        logging.error(f"Error generating registration trend: {str(e)}")
        return {'labels': [], 'values': []}

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
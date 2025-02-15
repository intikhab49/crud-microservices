from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Import models
from models import User

# Create tables if not exists
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    try:
        logger.debug("Fetching dashboard data")

        # Calculate statistics
        stats = {
            'total_users': db.session.query(User).count(),
            'new_users_today': db.session.query(User).filter(
                User.created_at >= datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            ).count(),
            'top_domain': "example.com"
        }

        # Get top email domain
        users = User.query.all()
        if users:
            domains = [user.email.split('@')[1] for user in users]
            stats['top_domain'] = Counter(domains).most_common(1)[0][0]

        # Get recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

        # Calculate registration trend
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=6)

        daily_counts = db.session.query(
            func.date(User.created_at).label('date'),
            func.count().label('count')
        ).filter(
            User.created_at >= start_date
        ).group_by(
            func.date(User.created_at)
        ).all()

        # Prepare chart data
        dates = []
        counts = []
        current_date = start_date

        count_dict = {date.strftime('%Y-%m-%d'): count for date, count in daily_counts}

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            dates.append(date_str)
            counts.append(count_dict.get(date_str, 0))
            current_date += timedelta(days=1)

        chart_data = {
            'labels': dates,
            'values': counts
        }

        return render_template('dashboard.html',
                               stats=stats,
                               recent_users=recent_users,
                               chart_data=chart_data)

    except SQLAlchemyError as e:
        logger.error(f"Database error in dashboard: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in dashboard route: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        logger.info(f"Deleted user with ID: {user_id}")
        return jsonify({'message': 'User deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in delete_user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Name and email are required'}), 400

        if not isinstance(data['name'], str) or not isinstance(data['email'], str):
            return jsonify({'error': 'Invalid data types'}), 400

        if len(data['name'].strip()) == 0 or len(data['email'].strip()) == 0:
            return jsonify({'error': 'Name and email cannot be empty'}), 400

        existing_user = User.query.filter(User.email == data['email'].strip(), User.id != user_id).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        user.name = data['name'].strip()
        user.email = data['email'].strip()
        db.session.commit()
        
        logger.info(f"Updated user with ID: {user_id}")
        return jsonify(user.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in update_user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        if not data or 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Name and email are required'}), 400

        if not isinstance(data['name'], str) or not isinstance(data['email'], str):
            return jsonify({'error': 'Invalid data types'}), 400

        if len(data['name'].strip()) == 0 or len(data['email'].strip()) == 0:
            return jsonify({'error': 'Name and email cannot be empty'}), 400

        existing_user = User.query.filter_by(email=data['email'].strip()).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400

        user = User(name=data['name'].strip(), email=data['email'].strip())
        db.session.add(user)
        db.session.commit()

        logger.info(f"Created user with ID: {user.id}")
        return jsonify(user.to_dict()), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in create_user: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

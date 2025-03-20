#!/bin/sh
echo "Starting container..."

# Wait for PostgreSQL readiness
for i in $(seq 1 15); do
    if pg_isready -h postgres -p 5432 -U postgres; then
        echo "Database ready"
        break
    fi
    echo "Waiting for postgres service... (attempt $i/15)"
    sleep 5
done

# Initialize the database
echo "Initializing database..."
python -c "from app import db, initialize_database; initialize_database()"

echo "Database is ready, starting Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:5000 app:app --timeout 120 --access-logfile -
#!/bin/sh
echo "Starting Nginx with dependency verification..."

# Verify configuration syntax first
nginx -t || exit 1

# Wait for web service
echo "Checking web service..."
while ! nc -z web 5000; do
    echo "Web service not ready - retrying in 5 seconds..."
    sleep 5
done

# Wait for logging service
echo "Checking logging service..."
while ! nc -z logging-service 5001; do
    echo "Logging service not ready - retrying in 5 seconds..."
    sleep 5
done

echo "All dependencies verified, starting Nginx"
exec nginx -g 'daemon off;'
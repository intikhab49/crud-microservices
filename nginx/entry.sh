#!/bin/sh
echo "Starting Nginx container..."
echo "Network details:"
exec nginx -g "daemon off;" 
ip addr show
echo "DNS configuration:"
cat /etc/resolv.conf

# Add retry logic for web service
echo "Resolving web service..."
for i in $(seq 1 15); do
    if nslookup web 127.0.0.11; then
        echo "Successfully resolved web on attempt $i"
        break
    else
        echo "Failed to resolve web on attempt $i, retrying in 5s..."
        sleep 5
    fi
done

echo "Waiting for web healthcheck..."
until curl -f --connect-timeout 10 http://web:5000/health; do
    echo "Waiting for web service... $(date)"
    sleep 5
done

echo "web is up, starting nginx"
exec nginx -g "daemon off;"
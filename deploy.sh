#!/bin/bash

# Remove existing stack
echo "Removing stack..."
docker stack rm my-app

# Wait for cleanup
echo "Waiting for resource cleanup..."
sleep 15  # Increased from 10 to 15 seconds

# Force remove lingering network if exists
if docker network inspect app-network >/dev/null 2>&1; then
    echo "Removing existing app-network..."
    docker network rm app-network 2>/dev/null || true
fi

# Prune all unused resources
echo "Pruning unused resources..."
docker system prune -af --volumes

# Deploy stack (networks will be created automatically)
echo "Deploying stack..."
docker stack deploy -c docker-compose.yml my-app

# Monitor services with improved formatting
watch -n 2 '
echo "=== Services ==="
docker service ls
echo ""
echo "=== Network Details ==="
docker network inspect app-network --format "{{range .Containers}}{{.Name}} {{.IPv4Address}}{{\"\n\"}}{{end}}"
'

# CRUD Microservices

A scalable CRUD application built with microservices, deployable on **Kubernetes** (with Flannel overlay networking) or **Docker Swarm**. Features `nginx` as a reverse proxy, a `web` app for CRUD operations, a `logging-service` for event tracking, and `postgres` with persistent storage.

## Overview
This project is a microservices-based CRUD app for managing users via a web interface and REST API. It supports dual orchestration with Kubernetes (using Flannel) and Docker Swarm, and includes a dedicated logging service for observability.

### Components
- **nginx**: Reverse proxy routing requests to the web app and serving static files.
- **web**: Flask app handling CRUD operations (`/users`) and a web UI.
- **postgres**: Database with persistent storage for user data.
- **logging-service**: Dedicated service logging events to `crud-logs.log` via `/logs`.

### Features
- **CRUD Operations**: Create, read, update, and delete users via `/users` API and UI.
- **Logging**: Events (e.g., user creation) logged to a separate service.
- **Dual Orchestration**: Runs on Kubernetes with Flannel overlay or Docker Swarm with its built-in overlay network.
- **Persistent Storage**: Postgres data survives restarts.

## File Structure

      crud-microservices/
      ├── app.py                         # Web app (Flask CRUD)
      ├── Dockerfile                    # Web app Dockerfile
      ├── requirements.txt              # Web app dependencies
      ├── static/                       # Static files (e.g., CSS)
      │   └── example.css
     ├── templates/                    # HTML templates
     │    └── index.html
     ├── web-deployment.yaml           # Web deployment and service (Kubernetes)
    ├── web-to-postgres-policy.yaml   # Network policy for web-to-postgres access
    ├── postgres-deployment.yaml      # Postgres deployment and service (Kubernetes)
     ├── nginx/                        # Nginx configuration
     │   ├── default.conf             # Nginx default config (optional)
     │   ├── Dockerfile               # Nginx Dockerfile
      │   ├── entry.sh                 # Nginx entry script
     │   └── nginx.conf               # Nginx main config
     ├── nginx-deployment.yaml         # Nginx deployment and service (Kubernetes)
    ├── logging-service/              # Logging service
    │   ├── Dockerfile               # Logging service Dockerfile
     │   ├── log_service.py           # Logging service script
    │   └── requirements.txt         # Logging service dependencies
    ├── logging-deployment.yaml       # Logging service deployment and service (Kubernetes)
     ├── docker-compose.yml            # Docker Compose file (optional, for local dev)
    ├── deploy.sh                     # Deployment script (if used)
    ├── start.sh                      # Start script (if used)
    ├── default.conf                  # Additional Nginx config (optional)
    ├── generated-icon.png            # Icon file (optional)
    ├── main.py                       # Alternative main script (optional)
     ├── models.py                     # Database models (optional)
    ├── network-policy.yaml           # Additional network policy (optional)
     ├── pod_diag.txt                  # Pod diagnostics (optional)
     ├── pyproject.toml                # Python project config (optional)
    ├── uv.lock                       # Dependency lock file (optional)
    ├── replit.nix                    # Replit config (optional)
     └── pycache/                  # Python cache (ignored)
    text

## Prerequisites
- **Docker**: For building images.
- **Minikube**: For Kubernetes deployment.
- **kubectl**: For managing Kubernetes.
- **Docker Swarm**: For Swarm deployment.
- **Git**: For cloning the repo.

## Setup Instructions

### Clone the Repository
```bash
git clone https://github.com/intikhab49/crud-microservices.git
cd crud-microservices
Option 1: Kubernetes (Minikube with Flannel)

    Start Minikube with Flannel:
    bash

minikube start --network-plugin=cni --cni=flannel --memory=4096
Build and Load Docker Images:

    Web App:
    bash

docker build -t intikhab49/myapp-web:v3.2 .
minikube image load intikhab49/myapp-web:v3.2
Nginx:
bash
cd nginx
docker build -t intikhab49/new-nginx-name:v1.1 .
minikube image load intikhab49/new-nginx-name:v1.1
cd ..
Logging Service:
bash

    cd logging-service
    docker build -t intikhab49/logging-service:v3.1 .
    minikube image load intikhab49/logging-service:v3.1
    cd ..

##Deploy to Minikube:
bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f web-deployment.yaml
kubectl apply -f nginx-deployment.yaml
kubectl apply -f logging-deployment.yaml
kubectl apply -f web-to-postgres-policy.yaml  # Optional network policy
Access the App:
bash
minikube service nginx --url

    Example: http://192.168.49.2:30242
    Test:
    bash

        curl http://192.168.49.2:30242/                # Web UI
        curl http://192.168.49.2:30242/users          # List users
        curl -X POST http://192.168.49.2:30242/users -H "Content-Type: application/json" -d '{"name": "Intikhab", "email": "intikhab@example.com"}'  # Add user
        curl -X POST http://192.168.49.2:30242/logs -H "Content-Type: application/json" -d '{"event": "test"}'  # Log event

Option 2: Docker Swarm

    Initialize Swarm:
    bash

docker swarm init
Build Docker Images:

    Web App:
    bash

docker build -t intikhab49/myapp-web:v3.2 .
Nginx:
bash
cd nginx
docker build -t intikhab49/new-nginx-name:v1.1 .
cd ..
Logging Service:
bash
cd logging-service
docker build -t intikhab49/logging-service:v3.1 .
cd ..
Deploy Stack:
bash
docker stack deploy -c docker-stack.yml crud-app
Access the App:

    Find the host IP and test:
    bash

        curl http://<swarm-ip>:80/users

Usage

    Web UI: Visit the URL from Minikube or Swarm to manage users.
    API: Use /users for CRUD operations.
    Logs: Check crud-logs.log in the logging pod (Kubernetes):
    bash

kubectl exec -it <logging-pod-name> -- cat /app/crud-logs.log

    Or in Swarm, inspect the container logs:
    bash

        docker service logs crud-app_logging-service

Contributing

Feel free to fork, submit issues, or send pull requests to enhance this project!
License

MIT License - see  if added.
text

---

### Steps to Update Your Repo
1. **Replace `README.md`**:
   ```bash
   cd ~/CRUD/crud-app1
   nano README.md

    Paste the above content, save, and exit.

    Commit and Push:
    bash

    git add README.md
    git commit -m "Update README with current file structure, Flannel, Docker Swarm, and logging service"
    git push origin main
    Verify:
        Check https://github.com/intikhab49/crud-microservices to see the new README.md.

Notes

    File Structure: Matches your ls output exactly, including optional files like docker-compose.yml, deploy.sh, etc.
    Flannel: Added to Kubernetes setup with --cni=flannel.
    Docker Swarm: Included with a sample docker-stack.yml (you’ll need to add it to your repo if you want Swarm support).
    Prometheus: Excluded since you haven’t added it yet.
    Extras: Kept optional files in the structure but didn’t detail them in setup unless critical.

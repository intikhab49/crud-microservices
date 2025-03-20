# CRUD Microservices App

A Kubernetes-based CRUD app running on Minikube with Flannel overlay networking.

## Components
- **nginx**: Reverse proxy serving static files and routing to `web`.
- **web**: Flask app handling CRUD operations.
- **postgres**: Database with persistent storage.

## Setup
1. Start Minikube:
   ```bash
   minikube start --network-plugin=cni --cni=flannel --memory=4096
   cd nginx && docker build -t nginx-custom:latest . && minikube image load nginx-custom:latest
cd ../web && docker build -t web-app:latest . && minikube image load web-app:latest 
kubectl apply -f postgres-deployment.yaml
kubectl apply -f web-deployment.yaml
kubectl apply -f nginx-deployment.yaml
minikube service nginx --url
curl <URL>/users

![Build Status](https://github.com/intikhab49/crud-microservices/actions/workflows/deploy.yml/badge.svg)](https://github.com/intikhab49/crud-microservices/actions)















# User Management System

A full-stack CRUD application built with Flask and PostgreSQL, providing robust user management and data persistence.

## Features
- User management (Create, Read, Update, Delete)
- Dashboard with user statistics
- Registration trend visualization
- Dark theme UI with Bootstrap

## Running Locally with Docker

1. Clone the repository
2. Make sure you have Docker and Docker Compose installed
3. From the project directory, run:
   ```bash
   docker-compose up --build
   ```
4. Access the application at `http://localhost:5000`

## Development without Docker (on Replit)

The application is already configured to run on Replit:
1. The Flask server runs on port 5000
2. PostgreSQL database is automatically configured
3. All required dependencies are pre-installed

## Environment Variables

The following environment variables are required:
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_SECRET_KEY`: Secret key for Flask sessions

When running with Docker, these are automatically configured in the docker-compose.yml file.

## Project Structure
```
.
├── app.py              # Main Flask application
├── models.py           # Database models
├── static/            
│   ├── css/           # Stylesheets
│   └── js/            # JavaScript files
├── templates/          # HTML templates
├── Dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose configuration
```

## Tech Stack
- Backend: Python Flask
- Database: PostgreSQL
- Frontend: Vanilla JavaScript
- UI Framework: Bootstrap

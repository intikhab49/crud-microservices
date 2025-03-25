# CRUD Microservices App
<<<<<<< HEAD
=======

A scalable CRUD app built with microservices, deployable on **Kubernetes** (with Flannel overlay) or **Docker Swarm**. Features `nginx` as a reverse proxy, a `web` app for CRUD operations, and `postgres` with persistent storage.

## Components
- **nginx**: Reverse proxy routing to `web` and serving static files.
- **web**: Flask app handling CRUD API (`/users`).
- **postgres**: Database with persistent storage.

## Features
- **Dual Orchestration**: Runs on Kubernetes (Minikube) or Docker Swarm.
- **Overlay Networking**: Flannel VXLAN on Kubernetes, Swarm’s built-in overlay on Docker.
- **Persistent Storage**: Postgres data survives restarts.
- **Monitoring Ready**: Add Prometheus/Loki/Grafana for observability (see [Monitoring](#monitoring)).

## Prerequisites
- Docker
- Minikube (for Kubernetes)
- Docker Swarm (for Swarm mode)
- Git

## Setup

### Kubernetes (Minikube)
1. **Start Minikube**:
   ```bash
   minikube start --network-plugin=cni --cni=flannel --memory=4096
   cd nginx && docker build -t nginx-custom:latest . && minikube image load nginx-custom:latest
   cd ../web && docker build -t web-app:latest . && minikube image load web-app:latest
   kubectl apply -f postgres-deployment.yaml
   kubectl apply -f web-deployment.yaml
   kubectl apply -f nginx-deployment.yaml
###docker swarm  
         
    docker swarm init
    cd nginx && docker build -t nginx-custom:latest .
    cd ../web && docker build -t web-app:latest .
    docker stack deploy -c docker-stack.yml crud-app
# User Management System
>>>>>>> origin/main

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
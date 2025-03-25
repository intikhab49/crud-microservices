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
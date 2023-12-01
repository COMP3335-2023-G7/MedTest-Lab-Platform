#!/bin/bash



echo "Pulling latest changes from Git..."
git pull

echo "Building and starting Docker containers..."
docker-compose up -d --build


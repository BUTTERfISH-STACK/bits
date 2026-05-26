#!/bin/bash
set -e

echo "Starting local dev environment..."

docker compose up -d db redis redpanda adminer

echo "Waiting for Postgres to initialize..."
sleep 10

docker compose up -d ollama inference_gateway

echo "Local services started."

echo "Visit Adminer: http://localhost:8080 to view Postgres."

echo "Inference gateway: http://localhost:8081/v1/assistant/chat"

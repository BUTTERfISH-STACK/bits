#!/bin/bash
set -e

# Simple test script to call the assistant endpoint
URL=http://localhost:8081/v1/assistant/chat
PAYLOAD='{"session_id":"s1","user_id":"22222222-2222-2222-2222-222222222222","tenant_id":"11111111-1111-1111-1111-111111111111","prompt":"Give me a one-paragraph summary of the latest interaction with Acme and suggested next steps."}'

curl -s -X POST "$URL" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .

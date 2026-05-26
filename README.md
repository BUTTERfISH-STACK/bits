# README - Local Dev

Prerequisites:
- Docker Desktop installed and running
- Git

Quickstart:
1. Clone repo and change to project dir
2. Copy .env or edit values
3. ./scripts/start_local.sh
4. Apply DB migrations: ./scripts/apply_migrations.sh
5. Access Adminer at http://localhost:8080 (Postgres)
6. Test assistant endpoint:
   curl -X POST http://localhost:8081/v1/assistant/chat -H "Content-Type: application/json" -d '{"session_id":"s1","user_id":"u1","tenant_id":"t1","prompt":"Summarize lead status for Acme"}'

Notes:
- Ollama image must be available and models placed in ./models
- If Docker not available, run services manually in cloud or local equivalents

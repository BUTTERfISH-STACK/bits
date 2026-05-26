# README - Local run order and troubleshooting

1. Prerequisites
- Docker Desktop
- Node.js + npm for frontend

2. Start local stack
- docker compose up -d db redis redpanda adminer ollama
- docker compose up -d cv_handler cv_processor inference_gateway

3. Apply DB migrations and seed (if not auto-run)
- ./scripts/apply_migrations.sh
- psql -h localhost -U crm_user -d crm_dev -f services/db/migrations/002_seed_sample_data.sql
- psql -h localhost -U crm_user -d crm_dev -f services/db/rls_helpers.sql

4. Run frontend
- cd apps/assistant
- npm install
- npm run dev

5. Upload CV
- Use frontend Upload page or curl script:
  curl -F "file=@path/to/resume.pdf" -F "job_title=Product Manager" -F "industry=Tech / SaaS" http://localhost:8090/v1/tenants/11111111-1111-1111-1111-111111111111/cv/upload

6. Monitor job
- GET http://localhost:8090/v1/tenants/11111111-1111-1111-1111-111111111111/cv/{job_id}
- Download result: http://localhost:8090/v1/tenants/11111111-1111-1111-1111-111111111111/cv/{job_id}/download

Troubleshooting
- 404 on upload: ensure cv_handler is healthy (GET /health) and reachable at port 8090.
- Worker not processing: ensure cv_processor is running and can reach Ollama. Check logs.
- Ollama 404: confirm Ollama container running and model is loaded in ./models.
- PDF generation errors: ensure weasyprint dependencies are installed in cv_processor container (libcairo2, pango).

Security notes
- Validate and scan uploaded files for malware in production.
- Enforce file size limits and content-type checks.

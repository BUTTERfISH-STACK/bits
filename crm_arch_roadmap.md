CRM SaaS Architecture & Implementation Roadmap

Overview
This document is a step-by-step, actionable workflow to build the high-performance multi-tenant CRM SaaS integrating the Ollama-served Qwen3.5-9B-DeepSeek (GGUF Q4_K_M) model as the primary intelligent backend and customer-facing assistant. It is intended for engineering and infra teams and contains infra commands, IaC skeletons, database schema, API contracts, model integration logic, deployment patterns, testing and validation procedures, and an implementation timeline.

Assumptions and defaults (professional judgment)
- Cloud: AWS (adjustable to GCP/Azure); Kubernetes on EKS.
- Primary OLTP: PostgreSQL (managed RDS); Event streaming: Kafka (MSK) or managed alternative; Object store: S3.
- Vector DB: Milvus (or pgvector if prefer Postgres-based vector index); cache: Redis.
- CI/CD: GitHub Actions; IaC: Terraform.

Phases and step-by-step workflow
Phase 0 — Preparation (completed)
- Deliverables: requirements doc, tenancy model decision (shared schema + RLS default), compliance matrix (GDPR/SOC2 baseline), cost estimate and POC plan for Ollama.

Phase 1 — Base infra & foundation (2–3 weeks)
Goals: reliable infra, K8s cluster, persistence, basic security and CI/CD.
Tasks (with concrete actions & sample commands):
1. Create Terraform repository layout
  - Directory: infra/terraform
  - Files: main.tf, variables.tf, providers.tf, modules/eks, modules/rds, modules/msk, modules/s3
  - Sample provider (AWS) in providers.tf:
    provider "aws" {
      region = var.aws_region
    }
2. Provision core infra (example commands):
  - terraform init
  - terraform plan -var-file=envs/prod.tfvars
  - terraform apply -auto-approve -var-file=envs/prod.tfvars
3. Provision EKS cluster (module) and GPU node pool for inference (taints/labels: inference=true,gpu=true).
4. Create RDS Postgres with multi-AZ for production and a smaller dev instance.
5. Create S3 buckets: event-lake, assets, model-artifacts with bucket policies and lifecycle rules.
6. Deploy MSK (or Confluent Kafka) cluster for event streaming.
7. Create IAM roles and KMS keys for encryption.

Phase 1 artifacts to commit
- infra/terraform/*
- README infra runbook (how to apply/dev/prod)
- kubeconfig for EKS (store secure instructions, not in repo)

Phase 2 — Platform core services (3–5 weeks)
Goals: core CRM services, auth, tenancy, DB, observability.
Tasks:
1. Bootstrap monorepo (or microservices) structure
  - services/{accounts,users,contacts,leads,activities,search,ingestion,inference-gateway,automations}
  - libs/{auth,db,logging,proto}
2. Authentication & tenant propagation
  - Use OIDC (Auth0/Keycloak). Implement middleware to extract tenant_id from JWT claims.
  - Enforce tenant context propagation via gRPC metadata and HTTP headers (X-Tenant-ID).
3. PostgreSQL schema (create core tables):
  - Provide SQL (see below) and RLS policies sample.
4. Implement REST + gRPC endpoints for core entities. Example endpoints:
  - GET /v1/tenants/{t}/leads
  - POST /v1/tenants/{t}/leads
  - gRPC internal: LeadService.ListLeads
5. Observability: deploy Prometheus, Grafana, OpenTelemetry collector; instrument services.

Postgres core schema (DDL excerpt)
-- tenants
CREATE TABLE tenants (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  plan TEXT,
  config JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  roles JSONB DEFAULT '[]',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- leads
CREATE TABLE leads (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  contact_id UUID,
  owner_id UUID,
  status TEXT,
  score DOUBLE PRECISION,
  score_reason JSONB,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- transcripts
CREATE TABLE transcripts (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  source TEXT,
  audio_url TEXT,
  text TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- predictions
CREATE TABLE predictions (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  model TEXT,
  input_hash TEXT,
  output JSONB,
  explainability JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

Indexes: create index on tenant_id for all tenant-scoped tables; GIN indexes for JSONB; create appropriate composite indexes for query patterns.

RLS sample
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON leads USING (tenant_id = current_setting('app.tenant_id')::uuid);

Phase 3 — Data pipeline & search (3–5 weeks)
Goals: real-time ingestion, event lake, feature store, vector DB.
Tasks:
1. Connectors
  - Build connector microservices for email (IMAP), webhooks, Twilio, Salesforce/HubSpot via OAuth.
  - Emit standardized events to Kafka topics: tenant.{tenant_id}.leads, tenant.{tenant_id}.interactions, tenant.{tenant_id}.transcripts
2. Event bus patterns
  - Schema registry (Avro/Protobuf) for events.
  - Topics: leads, activities, transcripts, document_ingest
3. Streaming processors
  - Implement stream consumers (Kafka Streams/Flink) for enrichment, feature computation.
4. Feature store
  - Implement low-latency feature store in Redis keyed by tenant_id:object_id -> feature_map
  - Materialized batch views in Postgres or ClickHouse for analytics.
5. Vector DB & embedding pipeline
  - Deploy Milvus or use pgvector. Create per-tenant partitions/collections.
  - Chunking strategy: split transcripts/documents into 500–1500 token chunks with overlap.
  - Embeddings: deploy a dedicated embedding model (recommend smaller GGUF embedding model or use Ollama if capable). Batch embeddings with concurrency limits.
  - Upsert vectors into vector DB with metadata: {tenant_id, ref_type, ref_id, chunk_index}

Phase 4 — Model infra & Inference Gateway (3–6 weeks)
Goals: Ollama deployment, inference gateway, RAG orchestration, streaming responses.
Tasks:
1. Ollama deployment
  - Create K8s GPU node pool; set tolerations and node selectors.
  - Containerize Ollama runtime (if required) and the model artifact gguf files on a shared PV or local disk of GPU nodes.
  - Expose an internal REST/gRPC API only available inside VPC.
2. Inference Gateway responsibilities
  - Auth & tenancy enforcement
  - Query vector DB, fetch top-K docs, fetch structured context (lead/opportunity state), fetch real-time features
  - Compose RAG prompt using templates and system-level constraints
  - Send prompt to Ollama inference service, stream tokens to client via WebSocket/SSE
  - Support function-call structured outputs (JSON) for suggested actions
  - Rate-limit & batch prompts when possible
3. Example inference request (HTTP) to Ollama
POST http://ollama.internal/v1/generate
Headers: Authorization: Bearer <svc-token>
Body: {"model":"Qwen3.5-9B-DeepSeek","prompt":"<assembled prompt>","max_tokens":512,"temperature":0.0}
Parse streaming response and map to assistant UI events.
4. Embedding service example
POST /internal/embeddings
Body: {tenant_id, texts: ["..."], model:"s-embedding-small"}
Response: embeddings array

Phase 5 — AI features (lead scoring, RAG assistant, automations) (4–8 weeks)
Goals: implement AI-driven features and connect them to CRM UI and workflows.
Tasks:
1. Automated lead scoring
  - Offline: extract historical labeled data from event lake and train LightGBM/XGBoost.
  - Store model in MLflow; compute SHAP explainability values and store in predictions.explainability.
  - Online serving: deploy model as REST gRPC microservice; cache results in Redis; stream updates to leads table via Kafka.
  - Example scoring endpoint: POST /v1/tenants/{t}/predict/lead_score {lead_id}
2. Conversational sales intelligence
  - STT pipeline: use Whisper or commercial STT to produce transcripts, store transcripts, chunk & embed.
  - Real-time assistant: during a call stream live transcript chunks into inference gateway for on-the-fly suggestions.
  - Post-call briefing: generate summary, objection list, next steps, and suggested tasks.
3. Autonomous workflows
  - Use Temporal.io for workflow orchestration. Define activities for external actions (send_email, create_task, update_record).
  - LLM returns JSON function calls; gateway validates and submits activity to Temporal.
  - Human-in-the-loop: require confirmation for sensitive actions (config per tenant).

Phase 6 — Hardening, scale, enterprise polish (ongoing)
Tasks:
- Multi-region deployments, DR plans, SLO/SLAs, canary rollouts for model changes, advanced RBAC, audit exports, tenant billing.

APIs: canonical contracts (OpenAPI stubs)
- Authentication
  POST /oauth/token
- CRM
  GET /v1/tenants/{t}/leads
  GET /v1/tenants/{t}/leads/{id}
  POST /v1/tenants/{t}/leads
- Assistant
  POST /v1/tenants/{t}/assistant/chat
    Request: {session_id:, user_id:, prompt:, context_hint: {account_id, lead_id}, tools: ["create_task"]}
    Response: {message_id, stream_url, citations: [{doc_id, score}], suggested_actions: [{type, payload}]}
- Embeddings
  POST /internal/embeddings {texts: []}
  Response: embeddings[]
- Vector search
  POST /internal/vector/search {tenant_id, query_embedding, top_k}
  Response: [{ref_id, score, metadata}]

Prompt engineering & templates
- System persona template (always prepend):
"You are the enterprise sales assistant for <tenant_name>. Use only provided documents and structured CRM fields. Never invent contact emails or phone numbers. If uncertain, ask for clarification."

- RAG prompt construction pattern:
[System persona]
[Structured context in JSON: lead fields, owner, last_activity, lead.score]
[Top-K retrieved documents with source and timestamp]
[Assistant instructions: produce a short recommended plan (3 bullets), suggested next actions (structured JSON), and 2-sentence sales script]

Security & privacy measures
- PII redaction pipe: detect PII using regex + model-based detectors; redact/sanitize before sending to LLM if tenant disallows.
- Tenant opt-out: per-tenant toggle to disable sending full context to LLM; in that case rely on stored embeddings/summarized contexts.
- mTLS between services, API keys for internal services, IAM for infra.
- Audit logs: append-only, immutable store (S3 or append-only DB) with indices for search.

Testing strategy
- Unit tests for all services and schema migration tests.
- Integration tests: use local Kafka (testcontainers), local Milvus/pgvector, and Ollama dev container for end-to-end tests.
- Load tests: k6 or Locust to test inference gateway throughput; run vector DB search load test.
- Model validation: regression tests for lead scoring (AUC thresholds), and hallucination/regression tests for assistant outputs.

Observability and drift monitoring
- Metrics: inference latency, token counts, top-K recall, vector DB query latency, GPU utilization, model drift metrics (distribution distances), feature-nan rates.
- Dashboards: Grafana dashboards for infra and model metrics.
- Alerts: Slack/email for pipeline failures, data quality alerts, and model drift warnings.

Cost & performance optimizations
- Use quantized model (Q4_K_M) as chosen to reduce GPU memory and cost.
- Use small embedding model for vector creation; batch embeddings and use async workers.
- Cache frequent RAG responses and use result deduplication.
- Autoscale GPU node pool with KEDA/custom metrics.

Deployment & rollout patterns
- Model rollout: shadow traffic -> canary (5–10%) -> gradual increase while monitoring inference metrics and user feedback.
- Backoff strategy: if Ollama overloaded, fallback to cached briefings or a smaller CPU-based model.

Sample code snippets (pseudocode)
1. Vector ingestion (Python sketch):
from requests import post
chunks = chunk_text(transcript.text)
embs = embedding_service.embed(tenant_id, chunks)
for i, emb in enumerate(embs):
  milvus.upsert(collection, [{"id": f"{transcript.id}:{i}", "vector": emb, "metadata": {"tenant_id": tenant_id, "ref_id": transcript.id, "chunk": i}}])

2. Inference flow (pseudocode)
- Client -> /assistant/chat with context_hint
- Gateway does:
  tenant_ctx = auth.extract_tenant(jwt)
  struct_ctx = db.fetch_lead(tenant_ctx, lead_id)
  features = feature_store.get(tenant_id, lead_id)
  docs = vector_search(top_k=6, query=query_embedding)
  prompt = template.render(system, struct_ctx, features, docs, user_prompt)
  response = ollama.generate(prompt, stream=True)
  stream tokens back to client and persist message and audit log
  parse structured actions and push to Temporal for execution (if confirmed)

Operational runbooks (key items)
- On Ollama crash: restart pod, check GPU node health, rotate to spare nodes.
- Vector DB corruption: failover to snapshot, rebuild partition from event lake.
- Data loss: recover from S3 event lake + reingest pipeline.

Timeline (12–24 weeks baseline with small team)
- Weeks 0–2: Phase 0 (done)
- Weeks 2–6: Phase 1 infra + auth + basic CRM services
- Weeks 6–10: Phase 2 connectors + event bus + feature store
- Weeks 10–16: Phase 3 model infra (Ollama) + RAG + assistant UI
- Weeks 16–22: Phase 4 lead scoring + automations + Temporal
- Weeks 22+: Phase 5 hardening, enterprise features, multi-region

Team & responsibilities (recommended)
- Infra/SRE (1-2): terraform, k8s, network, GPUs
- Backend (2-4): microservices, db, ingestion
- ML/ML-Ops (1-2): feature store, training, model serving
- Frontend (1-2): Next.js assistant UI and dashboards
- Data engineer (1): connectors, streaming
- Security/compliance (shared): policy, audit

Deliverables checklist (minimum viable for pilot)
- EKS cluster, RDS Postgres, S3, Kafka
- Basic CRM: tenants, users, leads, contacts, activities
- Event ingestion from one connector (email or Twilio)
- Vector DB and embedding pipeline
- Ollama inference gateway with model deployed and assistant UI (chat streaming)
- Lead scoring offline + online endpoint
- Temporal integration for one automation
- Observability and runbooks

Files to commit and where
- docs/architecture/crm_arch_roadmap.md  <-- this document
- infra/terraform/*
- services/* microservice scaffolds
- models/mlflow/* artifacts

Next immediate engineering actions (first week)
1. Finalize AWS account and permissions, create IaC skeleton (infra/terraform) and push to repo.
2. Create EKS cluster and GPU node pool; test GPU node scheduling by deploying a small CUDA test container.
3. Deploy Postgres (dev) and run DDL to create core tables and RLS settings.
4. Spin up a dev Kafka instance (local or MSK dev), and validate producing and consuming test events.
5. Build a minimal inference-gateway stub that can call a local Ollama dev container with the model (or mock) to validate end-to-end chat streaming.

Appendices
- API OpenAPI stubs (generate with swagger editor)
- Terraform module examples for EKS, RDS, S3 (templates)
- Example Prompts and RAG templates (copy to docs/prompts.md)

Contact & handoff
- Produce a one-page architecture diagram (draw.io) and attach to docs/architecture.
- Prepare a demo script for pilot customers that includes signup, connector setup, sample call ingestion, and assistant interaction.

---
End of roadmap

-- services/db/migrations/003_create_cv_jobs.sql

CREATE TABLE cv_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  user_id UUID,
  original_filename TEXT,
  storage_path TEXT,
  job_title TEXT,
  industry TEXT,
  status TEXT DEFAULT 'pending',
  result_text TEXT,
  result_pdf_path TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_cv_jobs_tenant ON cv_jobs(tenant_id);

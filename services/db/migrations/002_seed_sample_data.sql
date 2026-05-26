-- services/db/migrations/002_seed_sample_data.sql

-- Sample seed data for local development

-- Tenant
INSERT INTO tenants (id, name, plan)
VALUES ('11111111-1111-1111-1111-111111111111', 'Acme Corporation', 'trial');

-- User
INSERT INTO users (id, tenant_id, email, roles)
VALUES ('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'alice@acme.example', '["admin"]');

-- Account
INSERT INTO accounts (id, tenant_id, name, domain, industry)
VALUES ('33333333-3333-3333-3333-333333333333', 'Acme Corp', 'acme.example', 'Manufacturing');

-- Contact
INSERT INTO contacts (id, tenant_id, account_id, name, email, phone, metadata)
VALUES ('44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'Bob Buyer', 'bob@acme.example', '+15551234567', '{"role":"Procurement"}');

-- Lead
INSERT INTO leads (id, tenant_id, contact_id, owner_id, status, score, score_reason, metadata)
VALUES ('55555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', 'open', 0.72, '{"top_features":[{"feature":"last_activity_days","value":2},{"feature":"email_click_rate","value":0.12}]}', '{"source":"webform"}');

-- Transcript (post-call)
INSERT INTO transcripts (id, tenant_id, source, audio_url, text)
VALUES ('66666666-6666-6666-6666-666666666666', '11111111-1111-1111-1111-111111111111', 'twilio_call_1', 's3://event-lake/acme/calls/call1.wav', 'Discussed pricing and timeline. Interested in pilot. Needs procurement approval by next week.');

-- Activity linking transcript
INSERT INTO activities (id, tenant_id, subject, type, actor_id, target_id, timestamp, transcript_id)
VALUES ('77777777-7777-7777-7777-777777777777', '11111111-1111-1111-1111-111111111111', 'Call with Bob Buyer', 'call', '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555555', now(), '66666666-6666-6666-6666-666666666666');

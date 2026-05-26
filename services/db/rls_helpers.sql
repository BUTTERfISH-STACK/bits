-- services/db/rls_helpers.sql

-- Usage: set tenant for current session
-- SELECT set_config('app.tenant_id', '11111111-1111-1111-1111-111111111111', true);

CREATE OR REPLACE FUNCTION app.set_tenant_session(tenant_uuid UUID) RETURNS void LANGUAGE sql AS $$
  SELECT set_config('app.tenant_id', tenant_uuid::text, true);
$$;

CREATE OR REPLACE FUNCTION app.clear_tenant_session() RETURNS void LANGUAGE sql AS $$
  SELECT set_config('app.tenant_id', '', true);
$$;

-- Example: grant execute to application role
-- GRANT EXECUTE ON FUNCTION app.set_tenant_session(UUID) TO crm_app_role;

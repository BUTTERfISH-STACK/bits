-- Run migrations against local Postgres
psql "host=localhost port=5432 dbname=crm_dev user=crm_user password=crm_pass" -f services/db/migrations/001_create_core_tables.sql

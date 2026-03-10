\set ON_ERROR_STOP on

\if :{?admin_email}
\else
\echo 'ERROR: admin_email is required'
\echo 'Usage: psql "$DATABASE_URL" -v admin_email=admin@example.com -v admin_password=StrongPass123! -f scripts/create_admin.sql'
\quit 1
\endif

\if :{?admin_password}
\else
\echo 'ERROR: admin_password is required'
\echo 'Usage: psql "$DATABASE_URL" -v admin_email=admin@example.com -v admin_password=StrongPass123! -f scripts/create_admin.sql'
\quit 1
\endif

CREATE EXTENSION IF NOT EXISTS pgcrypto;

WITH payload AS (
    SELECT
        :'admin_email'::text AS email,
        crypt(:'admin_password', gen_salt('bf', 12)) AS hashed_password,
        COALESCE(NULLIF(:'admin_full_name', ''), 'Administrator')::text AS full_name,
        upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 8)) AS referral_code
)
INSERT INTO users (
    email,
    hashed_password,
    full_name,
    is_active,
    is_superuser,
    referral_code
)
SELECT
    p.email,
    p.hashed_password,
    p.full_name,
    TRUE,
    TRUE,
    p.referral_code
FROM payload p
ON CONFLICT (email) DO UPDATE
SET
    hashed_password = EXCLUDED.hashed_password,
    is_active = TRUE,
    is_superuser = TRUE,
    full_name = COALESCE(EXCLUDED.full_name, users.full_name);

SELECT id, email, is_active, is_superuser
FROM users
WHERE email = :'admin_email';

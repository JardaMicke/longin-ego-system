INSERT INTO ego_profile (id, version, soul_hash, directives)
VALUES ('00000000-0000-0000-0000-000000000010', 'bootstrap', 'pending', '{}'::jsonb)
ON CONFLICT DO NOTHING;

INSERT INTO identity_audit (id, event, version, soul_hash, directives)
VALUES ('00000000-0000-0000-0000-000000000011', 'bootstrap', 'bootstrap', 'pending', '{}'::jsonb)
ON CONFLICT DO NOTHING;

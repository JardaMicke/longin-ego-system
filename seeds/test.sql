INSERT INTO ego_profile (id, version, soul_hash, directives)
VALUES ('00000000-0000-0000-0000-000000000001', 'test', 'test-hash', '{}'::jsonb)
ON CONFLICT DO NOTHING;

INSERT INTO identity_audit (id, event, version, soul_hash, directives)
VALUES ('00000000-0000-0000-0000-000000000002', 'boot', 'test', 'test-hash', '{}'::jsonb)
ON CONFLICT DO NOTHING;

INSERT INTO ui_layouts (layout_id, project_id, layout_data, version, is_active)
VALUES ('00000000-0000-0000-0000-000000000003', 'default', '{}'::jsonb, 1, TRUE)
ON CONFLICT DO NOTHING;

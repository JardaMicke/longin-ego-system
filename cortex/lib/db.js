import { randomUUID } from "crypto";
import { readFileSync } from "fs";
import { Pool } from "pg";

let pool;

function readSecret(name) {
  const value = process.env[name];
  if (value) {
    return value;
  }
  const filePath = process.env[`${name}_FILE`];
  if (!filePath) {
    return undefined;
  }
  try {
    const content = readFileSync(filePath, "utf8").trim();
    return content || undefined;
  } catch (error) {
    throw new Error(`Secret file read failed for ${name}: ${error}`);
  }
}

function readProfiled(name, profile) {
  const key = `${profile.toUpperCase()}_${name}`;
  const value = process.env[key];
  if (value) {
    return value;
  }
  const filePath = process.env[`${key}_FILE`];
  if (filePath) {
    try {
      const content = readFileSync(filePath, "utf8").trim();
      return content || undefined;
    } catch (error) {
      throw new Error(`Secret file read failed for ${key}: ${error}`);
    }
  }
  return readSecret(name);
}

function getPool() {
  if (!pool) {
    const profile = process.env.LONGIN_ENV || "dev";
    const dsn = readProfiled("POSTGRES_DSN", profile) || readProfiled("DATABASE_URL", profile);
    if (!dsn) {
      throw new Error("POSTGRES_DSN is not configured");
    }
    pool = new Pool({ connectionString: dsn });
  }
  return pool;
}

async function ensureSchema() {
  const client = getPool();
  await client.query(
    "CREATE TABLE IF NOT EXISTS ui_layouts (layout_id UUID PRIMARY KEY, project_id TEXT NOT NULL, layout_data JSONB NOT NULL, version INTEGER NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE (project_id, version))"
  );
  await client.query(
    "CREATE INDEX IF NOT EXISTS idx_ui_layouts_project_active ON ui_layouts (project_id, is_active)"
  );
}

export async function getLayout(projectId) {
  await ensureSchema();
  const client = getPool();
  const result = await client.query(
    "SELECT layout_data, version FROM ui_layouts WHERE project_id = $1 AND is_active = TRUE ORDER BY version DESC LIMIT 1",
    [projectId]
  );
  if (result.rows.length === 0) {
    return null;
  }
  return { data: result.rows[0].layout_data, version: result.rows[0].version };
}

export async function saveLayout(projectId, data) {
  await ensureSchema();
  const pool = getPool();
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const current = await client.query(
      "SELECT COALESCE(MAX(version), 0) AS version FROM ui_layouts WHERE project_id = $1",
      [projectId]
    );
    const nextVersion = Number(current.rows[0].version) + 1;
    await client.query(
      "UPDATE ui_layouts SET is_active = FALSE, updated_at = NOW() WHERE project_id = $1 AND is_active = TRUE",
      [projectId]
    );
    await client.query(
      "INSERT INTO ui_layouts (layout_id, project_id, layout_data, version, is_active, created_at, updated_at) VALUES ($1, $2, $3, $4, TRUE, NOW(), NOW())",
      [randomUUID(), projectId, data, nextVersion]
    );
    await client.query("COMMIT");
    return nextVersion;
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

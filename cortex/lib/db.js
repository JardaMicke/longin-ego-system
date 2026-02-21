import { Pool } from "pg";

let pool;

function getPool() {
  if (!pool) {
    const dsn = process.env.POSTGRES_DSN || process.env.DATABASE_URL;
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
    "CREATE TABLE IF NOT EXISTS ui_layouts (path TEXT PRIMARY KEY, layout_data JSONB NOT NULL, updated_at TIMESTAMPTZ DEFAULT NOW())"
  );
}

export async function getLayout(path) {
  await ensureSchema();
  const client = getPool();
  const result = await client.query("SELECT layout_data FROM ui_layouts WHERE path = $1", [path]);
  if (result.rows.length === 0) {
    return null;
  }
  return result.rows[0].layout_data;
}

export async function saveLayout(path, data) {
  await ensureSchema();
  const client = getPool();
  await client.query(
    "INSERT INTO ui_layouts (path, layout_data, updated_at) VALUES ($1, $2, NOW()) ON CONFLICT (path) DO UPDATE SET layout_data = EXCLUDED.layout_data, updated_at = NOW()",
    [path, data]
  );
}

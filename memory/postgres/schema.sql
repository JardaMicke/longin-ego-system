CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS episodic_memory (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL,
    payload JSONB NOT NULL,
    importance DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS semantic_knowledge (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    embedding VECTOR(1536) NOT NULL,
    last_accessed TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ego_profile (
    id UUID PRIMARY KEY,
    version TEXT NOT NULL,
    soul_hash TEXT NOT NULL,
    directives JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    metadata JSONB NOT NULL,
    user_id TEXT
);

CREATE TABLE IF NOT EXISTS ui_layouts (
    layout_id UUID PRIMARY KEY,
    project_id TEXT NOT NULL,
    layout_data JSONB NOT NULL,
    version INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (project_id, version)
);

CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories (user_id);
CREATE INDEX IF NOT EXISTS idx_ui_layouts_project_active ON ui_layouts (project_id, is_active);

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Tuple, cast


@dataclass(frozen=True)
class PostgresConfig:
    """Účel: Konfigurace připojení k Postgresu.

    Vstupy/Výstupy: DSN připojení k databázi.
    Vedlejší efekty: Žádné.
    """
    dsn: str


class PostgresClient:
    """Účel: Poskytuje perzistenci a dotazy nad Postgres databází.

    Vstupy/Výstupy: Přijímá config, ukládá a čte data, vrací výsledky dotazů.
    Vedlejší efekty: Připojuje se k databázi a provádí SQL operace.
    """
    def __init__(self, config: PostgresConfig) -> None:
        self._config = config

    def _connect(self) -> Any:
        try:
            import psycopg
        except Exception as exc:
            raise RuntimeError(f"psycopg import failed: {exc}") from exc
        try:
            return psycopg.connect(self._config.dsn)
        except Exception as exc:
            raise RuntimeError(f"Postgres connection failed: {exc}") from exc

    def run_schema(self, schema_sql: str) -> None:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(schema_sql)
                conn.commit()
        except Exception as exc:
            raise RuntimeError(f"Schema execution failed: {exc}") from exc

    def vector_search(self, embedding: Iterable[float], limit: int = 5) -> List[Tuple[str, float]]:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT content, embedding <-> %s AS distance "
                        "FROM semantic_knowledge ORDER BY distance ASC LIMIT %s",
                        (list(embedding), limit),
                    )
                    return [(row[0], float(row[1])) for row in cur.fetchall()]
        except Exception as exc:
            raise RuntimeError(f"Vector search failed: {exc}") from exc

    def insert_identity(self, version: str, soul_hash: str, directives: Mapping[str, Any]) -> None:
        try:
            import uuid
            import json
        except Exception as exc:
            raise RuntimeError(f"Import failed: {exc}") from exc
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO ego_profile (id, version, soul_hash, directives) VALUES (%s, %s, %s, %s)",
                        (str(uuid.uuid4()), version, soul_hash, json.dumps(directives)),
                    )
                conn.commit()
        except Exception as exc:
            raise RuntimeError(f"Insert identity failed: {exc}") from exc

    def insert_identity_audit(
        self,
        event: str,
        version: str,
        soul_hash: str,
        directives: Mapping[str, Any],
    ) -> None:
        try:
            import uuid
            import json
        except Exception as exc:
            raise RuntimeError(f"Import failed: {exc}") from exc
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO identity_audit (id, event, version, soul_hash, directives) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (str(uuid.uuid4()), event, version, soul_hash, json.dumps(directives)),
                    )
                conn.commit()
        except Exception as exc:
            raise RuntimeError(f"Insert identity audit failed: {exc}") from exc

    def search_identity_audit(
        self,
        event: str | None = None,
        version: str | None = None,
        limit: int = 50,
    ) -> List[Tuple[str, str, str, Mapping[str, Any], Any]]:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    clauses = []
                    params: List[Any] = []
                    if event:
                        clauses.append("event = %s")
                        params.append(event)
                    if version:
                        clauses.append("version = %s")
                        params.append(version)
                    where = f"WHERE {' AND '.join(clauses)} " if clauses else ""
                    cur.execute(
                        "SELECT event, version, soul_hash, directives, created_at "
                        f"FROM identity_audit {where}ORDER BY created_at DESC LIMIT %s",
                        tuple(params + [limit]),
                    )
                    return [
                        (row[0], row[1], row[2], cast(Mapping[str, Any], row[3]), row[4])
                        for row in cur.fetchall()
                    ]
        except Exception as exc:
            raise RuntimeError(f"Identity audit search failed: {exc}") from exc

    def prune_identity_audit(
        self,
        older_than_days: int | None = None,
        keep_latest: int | None = None,
    ) -> int:
        if older_than_days is None and keep_latest is None:
            raise RuntimeError("Identity audit prune policy missing")
        deleted = 0
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    if older_than_days is not None:
                        cur.execute(
                            "DELETE FROM identity_audit "
                            "WHERE created_at < NOW() - (%s || ' days')::interval",
                            (int(older_than_days),),
                        )
                        deleted += int(getattr(cur, "rowcount", 0) or 0)
                    if keep_latest is not None:
                        cur.execute(
                            "DELETE FROM identity_audit "
                            "WHERE id IN (SELECT id FROM identity_audit "
                            "ORDER BY created_at DESC OFFSET %s)",
                            (int(keep_latest),),
                        )
                        deleted += int(getattr(cur, "rowcount", 0) or 0)
                conn.commit()
            return deleted
        except Exception as exc:
            raise RuntimeError(f"Identity audit prune failed: {exc}") from exc

    def insert_episodic(self, source: str, payload: Mapping[str, Any], importance: float) -> None:
        try:
            import uuid
            import json
        except Exception as exc:
            raise RuntimeError(f"Import failed: {exc}") from exc
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO episodic_memory (id, source, payload, importance) VALUES (%s, %s, %s, %s)",
                        (str(uuid.uuid4()), source, json.dumps(dict(payload)), float(importance)),
                    )
                conn.commit()
        except Exception as exc:
            raise RuntimeError(f"Insert episodic memory failed: {exc}") from exc

    def insert_semantic(self, content: str, tags: Iterable[str], embedding: Iterable[float]) -> None:
        try:
            import uuid
        except Exception as exc:
            raise RuntimeError(f"Import failed: {exc}") from exc
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO semantic_knowledge (id, content, tags, embedding) VALUES (%s, %s, %s, %s)",
                        (str(uuid.uuid4()), content, list(tags), list(embedding)),
                    )
                conn.commit()
        except Exception as exc:
            raise RuntimeError(f"Insert semantic memory failed: {exc}") from exc

    def insert_memory(
        self,
        content: str,
        embedding: Iterable[float],
        metadata: Mapping[str, Any],
        user_id: str | None = None,
    ) -> None:
        try:
            import uuid
            import json
        except Exception as exc:
            raise RuntimeError(f"Import failed: {exc}") from exc
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO memories (id, content, embedding, metadata, user_id) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (
                            str(uuid.uuid4()),
                            content,
                            list(embedding),
                            json.dumps(dict(metadata)),
                            user_id,
                        ),
                    )
                conn.commit()
        except Exception as exc:
            raise RuntimeError(f"Insert memory failed: {exc}") from exc

    def search_memories(
        self,
        embedding: Iterable[float],
        limit: int = 5,
        user_id: str | None = None,
    ) -> List[Tuple[str, float]]:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    if user_id:
                        cur.execute(
                            "SELECT content, embedding <-> %s AS distance "
                            "FROM memories WHERE user_id = %s ORDER BY distance ASC LIMIT %s",
                            (list(embedding), user_id, limit),
                        )
                    else:
                        cur.execute(
                            "SELECT content, embedding <-> %s AS distance "
                            "FROM memories ORDER BY distance ASC LIMIT %s",
                            (list(embedding), limit),
                        )
                    return [(row[0], float(row[1])) for row in cur.fetchall()]
        except Exception as exc:
            raise RuntimeError(f"Memory search failed: {exc}") from exc

    def upsert_ui_layout(
        self,
        project_id: str,
        layout_data: Mapping[str, Any],
        version: int,
        is_active: bool = True,
    ) -> None:
        try:
            import uuid
            import json
        except Exception as exc:
            raise RuntimeError(f"Import failed: {exc}") from exc
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO ui_layouts "
                        "(layout_id, project_id, layout_data, version, is_active) "
                        "VALUES (%s, %s, %s, %s, %s) "
                        "ON CONFLICT (project_id, version) DO UPDATE SET "
                        "layout_data = EXCLUDED.layout_data, "
                        "is_active = EXCLUDED.is_active, "
                        "updated_at = NOW()",
                        (
                            str(uuid.uuid4()),
                            project_id,
                            json.dumps(dict(layout_data)),
                            int(version),
                            bool(is_active),
                        ),
                    )
                conn.commit()
        except Exception as exc:
            raise RuntimeError(f"Upsert UI layout failed: {exc}") from exc

    def get_active_ui_layout(self, project_id: str) -> Mapping[str, Any] | None:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT layout_data FROM ui_layouts "
                        "WHERE project_id = %s AND is_active = TRUE "
                        "ORDER BY version DESC LIMIT 1",
                        (project_id,),
                    )
                    row = cur.fetchone()
                    if row is None:
                        return None
                    return cast(Mapping[str, Any], row[0])
        except Exception as exc:
            raise RuntimeError(f"Fetch UI layout failed: {exc}") from exc

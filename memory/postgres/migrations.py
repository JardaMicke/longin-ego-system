from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Callable, Dict, List, Optional, Protocol, Sequence, Tuple, cast


@dataclass(frozen=True)
class Migration:
    version: str
    path: Path
    checksum: str
    sql: str


class CursorProtocol(Protocol):
    def execute(self, query: str, params: Optional[Tuple[object, ...]] = None) -> None:
        ...

    def fetchall(self) -> Sequence[Tuple[object, ...]]:
        ...

    def __enter__(self) -> "CursorProtocol":
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        ...


class ConnectionProtocol(Protocol):
    def cursor(self) -> CursorProtocol:
        ...

    def commit(self) -> None:
        ...

    def __enter__(self) -> "ConnectionProtocol":
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        ...


class MigrationRunner:
    def __init__(
        self,
        dsn: str,
        migrations_dir: Path,
        connect: Optional[Callable[[], ConnectionProtocol]] = None,
    ) -> None:
        self._dsn = dsn
        self._migrations_dir = migrations_dir
        self._connect = connect or self._default_connect

    def _default_connect(self) -> ConnectionProtocol:
        try:
            import psycopg
        except Exception as exc:
            raise RuntimeError(f"psycopg import failed: {exc}") from exc
        try:
            return cast(ConnectionProtocol, psycopg.connect(self._dsn))
        except Exception as exc:
            raise RuntimeError(f"Postgres connection failed: {exc}") from exc

    def _load_migrations(self) -> List[Migration]:
        try:
            files = sorted(self._migrations_dir.glob("*.sql"))
        except Exception as exc:
            raise RuntimeError(f"Migration scan failed: {exc}") from exc
        migrations: List[Migration] = []
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as exc:
                raise RuntimeError(f"Migration read failed for {file_path.name}: {exc}") from exc
            checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
            migrations.append(Migration(version=file_path.name, path=file_path, checksum=checksum, sql=content))
        return migrations

    def apply_all(self) -> List[str]:
        migrations = self._load_migrations()
        applied: List[str] = []
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS schema_migrations ("
                        "version TEXT PRIMARY KEY, "
                        "checksum TEXT NOT NULL, "
                        "applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()"
                        ")"
                    )
                conn.commit()
                with conn.cursor() as cur:
                    cur.execute("SELECT version, checksum FROM schema_migrations")
                    existing_rows = cur.fetchall()
                existing: Dict[str, str] = {str(row[0]): str(row[1]) for row in existing_rows}
                for migration in migrations:
                    known_checksum = existing.get(migration.version)
                    if known_checksum:
                        if known_checksum != migration.checksum:
                            raise RuntimeError(f"Migration checksum mismatch for {migration.version}")
                        continue
                    with conn.cursor() as cur:
                        cur.execute(migration.sql)
                        cur.execute(
                            "INSERT INTO schema_migrations (version, checksum) VALUES (%s, %s)",
                            (migration.version, migration.checksum),
                        )
                    conn.commit()
                    applied.append(migration.version)
            return applied
        except Exception as exc:
            raise RuntimeError(f"Migration failed: {exc}") from exc


def apply_seed(
    dsn: str,
    seed_path: Path,
    connect: Optional[Callable[[], ConnectionProtocol]] = None,
) -> None:
    runner = MigrationRunner(dsn, seed_path.parent, connect=connect)
    try:
        content = seed_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Seed read failed for {seed_path.name}: {exc}") from exc
    try:
        with runner._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(content)
            conn.commit()
    except Exception as exc:
        raise RuntimeError(f"Seed apply failed: {exc}") from exc

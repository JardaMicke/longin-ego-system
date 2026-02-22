from memory.postgres.migrations import MigrationRunner, apply_seed


class FakeCursor:
    def __init__(self, rows=None) -> None:
        self.rows = rows or []
        self.queries = []
        self.params = []

    def execute(self, query, params=None) -> None:
        self.queries.append(query)
        self.params.append(params)

    def fetchall(self):
        return self.rows

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor
        self.commits = 0

    def cursor(self):
        return self._cursor

    def commit(self) -> None:
        self.commits += 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_migration_runner_applies_new_migration(tmp_path) -> None:
    migration_dir = tmp_path / "migrations"
    migration_dir.mkdir()
    migration_file = migration_dir / "001_init.sql"
    migration_file.write_text("CREATE TABLE demo(id INT);", encoding="utf-8")
    cursor = FakeCursor(rows=[])
    conn = FakeConnection(cursor)
    runner = MigrationRunner("dsn", migration_dir, connect=lambda: conn)
    applied = runner.apply_all()
    assert applied == ["001_init.sql"]
    assert any("schema_migrations" in query for query in cursor.queries)
    assert any("CREATE TABLE demo" in query for query in cursor.queries)


def test_migration_runner_detects_checksum_mismatch(tmp_path) -> None:
    migration_dir = tmp_path / "migrations"
    migration_dir.mkdir()
    migration_file = migration_dir / "001_init.sql"
    migration_file.write_text("CREATE TABLE demo(id INT);", encoding="utf-8")
    cursor = FakeCursor(rows=[("001_init.sql", "bad")])
    conn = FakeConnection(cursor)
    runner = MigrationRunner("dsn", migration_dir, connect=lambda: conn)
    try:
        runner.apply_all()
    except RuntimeError as exc:
        assert "checksum mismatch" in str(exc)
        return
    raise AssertionError("Expected RuntimeError")


def test_apply_seed_executes_script(tmp_path) -> None:
    seed_path = tmp_path / "seed.sql"
    seed_path.write_text("CREATE TABLE seeded(id INT);", encoding="utf-8")
    cursor = FakeCursor(rows=[])
    conn = FakeConnection(cursor)
    apply_seed("dsn", seed_path, connect=lambda: conn)
    assert any("CREATE TABLE seeded" in query for query in cursor.queries)

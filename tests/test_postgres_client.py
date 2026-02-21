from memory.postgres.client import PostgresClient, PostgresConfig


class FakeCursor:
    def __init__(self, rows=None, rowcounts=None) -> None:
        self.rows = rows or []
        self.rowcounts = rowcounts or []
        self.queries = []
        self.params = []
        self._index = 0
        self.rowcount = 0

    def execute(self, query, params=None) -> None:
        self.queries.append(query)
        self.params.append(params)
        if self._index < len(self.rowcounts):
            self.rowcount = self.rowcounts[self._index]
        else:
            self.rowcount = 0
        self._index += 1

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


def test_search_identity_audit_builds_filters(monkeypatch) -> None:
    rows = [("boot", "v1", "hash", {"who": "core"}, "2026-01-01")]
    cursor = FakeCursor(rows=rows)
    conn = FakeConnection(cursor)
    client = PostgresClient(PostgresConfig(dsn="dsn"))
    monkeypatch.setattr(client, "_connect", lambda: conn)
    result = client.search_identity_audit(event="boot", version="v1", limit=10)
    assert result == rows
    assert "FROM identity_audit" in cursor.queries[0]
    assert cursor.params[0] == ("boot", "v1", 10)


def test_prune_identity_audit_executes_policy(monkeypatch) -> None:
    cursor = FakeCursor(rowcounts=[2, 3])
    conn = FakeConnection(cursor)
    client = PostgresClient(PostgresConfig(dsn="dsn"))
    monkeypatch.setattr(client, "_connect", lambda: conn)
    deleted = client.prune_identity_audit(older_than_days=7, keep_latest=100)
    assert deleted == 5
    assert len(cursor.queries) == 2
    assert cursor.params[0] == (7,)
    assert cursor.params[1] == (100,)


def test_prune_identity_audit_requires_policy() -> None:
    client = PostgresClient(PostgresConfig(dsn="dsn"))
    try:
        client.prune_identity_audit()
    except RuntimeError as exc:
        assert "Identity audit prune policy missing" in str(exc)
        return
    raise AssertionError("Expected RuntimeError")

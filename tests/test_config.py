from kernel.config import read_bool, read_float, read_int, read_profiled, read_secret
from kernel.runtime import KernelRuntimeConfig


def test_read_secret_prefers_env(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_DSN", "dsn")
    assert read_secret("POSTGRES_DSN") == "dsn"


def test_read_secret_from_file(tmp_path, monkeypatch) -> None:
    secret_path = tmp_path / "secret.txt"
    secret_path.write_text("value", encoding="utf-8")
    monkeypatch.delenv("POSTGRES_DSN", raising=False)
    monkeypatch.setenv("POSTGRES_DSN_FILE", str(secret_path))
    assert read_secret("POSTGRES_DSN") == "value"


def test_read_profiled_overrides_base(tmp_path, monkeypatch) -> None:
    secret_path = tmp_path / "secret.txt"
    secret_path.write_text("profiled", encoding="utf-8")
    monkeypatch.setenv("PROD_POSTGRES_DSN_FILE", str(secret_path))
    monkeypatch.setenv("POSTGRES_DSN", "base")
    assert read_profiled("POSTGRES_DSN", "prod") == "profiled"


def test_read_bool_parses(monkeypatch) -> None:
    assert read_bool("true", False) is True
    assert read_bool("0", True) is False


def test_read_int_parses() -> None:
    assert read_int("12", 1) == 12


def test_read_float_parses() -> None:
    assert read_float("1.5", 1.0) == 1.5


def test_kernel_runtime_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("LONGIN_ENV", "dev")
    monkeypatch.setenv("DEV_REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEV_POSTGRES_DSN", "postgresql://user:pass@localhost/db")
    config = KernelRuntimeConfig.from_env()
    assert config.redis_url == "redis://localhost:6379/0"
    assert config.postgres_dsn == "postgresql://user:pass@localhost/db"
    assert config.enable_discovery is True

import json
import pytest

from kernel.security.identity_boot import IdentityBootConfig, IdentityBootLoader


class FakeBus:
    def __init__(self) -> None:
        self.data = {}

    def set_key(self, key: str, value: str) -> None:
        self.data[key] = value


class FakePostgresClient:
    def __init__(self) -> None:
        self.inserted = []
        self.audit = []

    def insert_identity(self, version: str, soul_hash: str, directives) -> None:
        self.inserted.append((version, soul_hash, directives))

    def insert_identity_audit(self, event: str, version: str, soul_hash: str, directives) -> None:
        self.audit.append((event, version, soul_hash, directives))


def test_identity_boot_persists_directives(tmp_path) -> None:
    soul_file = tmp_path / "soul.md"
    soul_file.write_text(
        "# VERSION\nv7\n\n# WHO AM I\nCore\n\n# PRIME DIRECTIVES\n- Stay safe\n\n# TONE OF VOICE\nClear\n",
        encoding="utf-8",
    )
    bus = FakeBus()
    postgres = FakePostgresClient()
    loader = IdentityBootLoader(IdentityBootConfig(soul_path=str(soul_file)))
    payload = loader.boot(bus, postgres)
    assert bus.data["SYS:SOUL:VERSION"] == "v7"
    directives = json.loads(bus.data["SYS:SOUL:DIRECTIVES"])
    assert directives["who_am_i"] == ["Core"]
    assert directives["prime_directives"] == ["Stay safe"]
    assert directives["tone_of_voice"] == ["Clear"]
    assert payload["version"] == "v7"
    assert postgres.inserted[0][0] == "v7"
    assert postgres.audit[0][0] == "boot"


def test_identity_boot_validates_required_sections(tmp_path) -> None:
    soul_file = tmp_path / "soul.md"
    soul_file.write_text(
        "# VERSION\nv7\n\n# WHO AM I\nCore\n\n# PRIME DIRECTIVES\n\n# TONE OF VOICE\nClear\n",
        encoding="utf-8",
    )
    bus = FakeBus()
    postgres = FakePostgresClient()
    loader = IdentityBootLoader(IdentityBootConfig(soul_path=str(soul_file)))
    with pytest.raises(RuntimeError, match="Identity boot validation failed"):
        loader.boot(bus, postgres)

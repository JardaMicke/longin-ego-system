from kernel.security.identity_firewall import IdentityConfig, IdentityFirewall


class FakeBus:
    def __init__(self) -> None:
        self.data = {}

    def set_key(self, key: str, value: str) -> None:
        self.data[key] = value


def test_identity_firewall_detects_changes(tmp_path) -> None:
    soul_file = tmp_path / "soul.md"
    soul_file.write_text("first", encoding="utf-8")
    bus = FakeBus()
    firewall = IdentityFirewall(IdentityConfig(soul_path=str(soul_file)), bus)
    assert firewall.has_changed() is False
    soul_file.write_text("second", encoding="utf-8")
    assert firewall.has_changed() is True

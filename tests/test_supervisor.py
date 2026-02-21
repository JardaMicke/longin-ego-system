from kernel.orchestration.supervisor import Supervisor, SupervisorConfig


class FakeBus:
    def __init__(self) -> None:
        self.messages = []

    def publish_stream(self, stream: str, payload):
        self.messages.append((stream, payload))
        return "1-0"


class FakeIdentity:
    def get_identity_state(self):
        return "hash-1", False


def test_supervisor_routes_to_inbox() -> None:
    bus = FakeBus()
    supervisor = Supervisor(SupervisorConfig(inbox_stream="SYS:INBOX"), bus, identity_firewall=FakeIdentity())
    message_id = supervisor.route({"tags": ["a"]}, {"data": "x"})
    assert message_id == "1-0"
    assert bus.messages[0][0] == "SYS:INBOX"


class ChangingIdentity:
    def get_identity_state(self):
        return "hash-2", True


def test_supervisor_publishes_identity_flush() -> None:
    bus = FakeBus()
    supervisor = Supervisor(
        SupervisorConfig(
            inbox_stream="SYS:INBOX",
            identity_flush_stream="SYS:MEMORY:FLUSH",
            identity_flush_min_interval_seconds=0.0,
        ),
        bus,
        identity_firewall=ChangingIdentity(),
    )
    supervisor.route({"tags": ["a"]}, {"data": "x"})
    streams = [stream for stream, _ in bus.messages]
    assert "SYS:MEMORY:FLUSH" in streams


def test_supervisor_throttles_identity_flush() -> None:
    bus = FakeBus()
    supervisor = Supervisor(
        SupervisorConfig(
            inbox_stream="SYS:INBOX",
            identity_flush_stream="SYS:MEMORY:FLUSH",
            identity_flush_min_interval_seconds=9999.0,
        ),
        bus,
        identity_firewall=ChangingIdentity(),
    )
    supervisor.route({"tags": ["a"]}, {"data": "x"})
    supervisor.route({"tags": ["a"]}, {"data": "x"})
    flushes = [stream for stream, _ in bus.messages if stream == "SYS:MEMORY:FLUSH"]
    assert len(flushes) == 1

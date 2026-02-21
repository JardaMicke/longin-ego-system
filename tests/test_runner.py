import pytest

from kernel.execution.runner import RunnerConfig, SiblingRunner
from kernel.security.airlock import Airlock, AirlockPolicy


class FakeContainerManager:
    def __init__(self) -> None:
        self.ran = False
        self.stopped = []
        self.logs = "ok"
        self.wait_raises = False

    def run_container(self, image: str, command: str, limits=None, env=None, volumes=None) -> str:
        self.ran = True
        return "cid-1"

    def wait_container(self, container_id: str, timeout: int = 0) -> int:
        if self.wait_raises:
            raise RuntimeError("timeout")
        return 0

    def get_logs(self, container_id: str) -> str:
        return self.logs

    def stop_container(self, container_id: str, timeout: int = 10) -> None:
        self.stopped.append(container_id)


def test_sibling_runner_rejects_blocked_imports() -> None:
    airlock = Airlock(AirlockPolicy(allowed_modules=set(), blocked_modules={"os"}))
    manager = FakeContainerManager()
    runner = SiblingRunner(airlock, manager, RunnerConfig())
    with pytest.raises(RuntimeError):
        runner.run("import os\nprint('x')")
    assert manager.ran is False


def test_sibling_runner_stops_on_timeout() -> None:
    airlock = Airlock(AirlockPolicy(allowed_modules=set(), blocked_modules={"os"}))
    manager = FakeContainerManager()
    manager.wait_raises = True
    runner = SiblingRunner(airlock, manager, RunnerConfig())
    with pytest.raises(RuntimeError):
        runner.run("print('ok')")
    assert manager.stopped == ["cid-1"]


def test_sibling_runner_returns_output() -> None:
    airlock = Airlock(AirlockPolicy(allowed_modules=set(), blocked_modules={"os"}))
    manager = FakeContainerManager()
    manager.logs = "hello"
    runner = SiblingRunner(airlock, manager, RunnerConfig())
    status, output = runner.run("print('ok')")
    assert status == 0
    assert output == "hello"

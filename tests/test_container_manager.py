from kernel.security.container_manager import ContainerManager


class FakeContainer:
    def __init__(self, container_id: str) -> None:
        self.id = container_id

    def stop(self, timeout: int) -> None:
        return None

    def remove(self, force: bool) -> None:
        return None

    def logs(self, stdout: bool, stderr: bool) -> bytes:
        return b"output"

    def wait(self, timeout: int) -> dict:
        return {"StatusCode": 0}


class FakeContainerCollection:
    def __init__(self) -> None:
        self.created = FakeContainer("container-1")

    def run(self, **kwargs):
        return self.created

    def get(self, container_id: str) -> FakeContainer:
        return FakeContainer(container_id)


class FakeDockerClient:
    def __init__(self) -> None:
        self.containers = FakeContainerCollection()


class FakeDockerModule:
    @staticmethod
    def from_env():
        return FakeDockerClient()


def test_container_manager_run_and_logs(monkeypatch) -> None:
    monkeypatch.setitem(__import__("sys").modules, "docker", FakeDockerModule())
    manager = ContainerManager()
    container_id = manager.run_container(image="python:3.11", command="echo hi")
    assert container_id == "container-1"
    assert manager.get_logs(container_id) == "output"
    assert manager.wait_container(container_id) == 0

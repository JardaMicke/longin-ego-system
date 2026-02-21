import types

from kernel.arbiter.core import Arbiter, ArbiterPolicy


def test_arbiter_allows_when_resources_ok(monkeypatch) -> None:
    fake_psutil = types.SimpleNamespace()
    fake_psutil.virtual_memory = lambda: types.SimpleNamespace(available=10 * 1024**3, total=32 * 1024**3)
    monkeypatch.setitem(__import__("sys").modules, "psutil", fake_psutil)
    monkeypatch.setitem(__import__("sys").modules, "pynvml", None)
    arbiter = Arbiter(ArbiterPolicy(min_free_gb=4.0, max_gpu_temp_c=80.0))
    assert arbiter.check_resources() is True


def test_arbiter_blocks_when_low_memory(monkeypatch) -> None:
    fake_psutil = types.SimpleNamespace()
    fake_psutil.virtual_memory = lambda: types.SimpleNamespace(available=1 * 1024**3, total=32 * 1024**3)
    monkeypatch.setitem(__import__("sys").modules, "psutil", fake_psutil)
    monkeypatch.setitem(__import__("sys").modules, "pynvml", None)
    arbiter = Arbiter(ArbiterPolicy(min_free_gb=4.0, max_gpu_temp_c=80.0))
    assert arbiter.check_resources() is False

from kernel.security.airlock import Airlock, AirlockPolicy


def test_airlock_allows_whitelisted_imports() -> None:
    policy = AirlockPolicy(allowed_modules={"math"}, blocked_modules={"os"})
    airlock = Airlock(policy)
    result = airlock.validate_code("import math")
    assert result.ok is True


def test_airlock_blocks_blocked_imports() -> None:
    policy = AirlockPolicy(allowed_modules=set(), blocked_modules={"os"})
    airlock = Airlock(policy)
    result = airlock.validate_code("import os")
    assert result.ok is False

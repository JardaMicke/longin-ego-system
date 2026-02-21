import pytest

from longin_sdk.core.exceptions import PermissionError
from longin_sdk.tools.net import SafeHttpClient


def test_safe_http_blocks_invalid_scheme() -> None:
    client = SafeHttpClient()
    with pytest.raises(PermissionError):
        client.get("ftp://example.com")

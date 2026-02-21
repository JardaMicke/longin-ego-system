from __future__ import annotations

from typing import Any, Dict, Type, cast


def pydantic_to_schema(model: Type[Any]) -> Dict[str, Any]:
    try:
        return cast(Dict[str, Any], model.model_json_schema())
    except Exception as exc:
        raise RuntimeError(f"Schema generation failed: {exc}") from exc

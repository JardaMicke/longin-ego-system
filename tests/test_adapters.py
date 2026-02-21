from pydantic import BaseModel

from longin_sdk.mcp.adapters import pydantic_to_schema


class SampleModel(BaseModel):
    name: str


def test_pydantic_to_schema() -> None:
    schema = pydantic_to_schema(SampleModel)
    assert schema["title"] == "SampleModel"

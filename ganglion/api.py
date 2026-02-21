from __future__ import annotations

from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ganglion.execution import LocalExecutor, SandboxExecutor
from ganglion.hardware import read_hardware_profile

app = FastAPI()


class SpawnRequest(BaseModel):
    command: str = Field(min_length=1)
    sandbox_mode: bool = True
    env_vars: Dict[str, str] = Field(default_factory=dict)


class SpawnResponse(BaseModel):
    exit_code: int
    output: str


def capabilities() -> Dict[str, object]:
    try:
        return read_hardware_profile()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Hardware probe failed: {exc}") from exc


def spawn(request: SpawnRequest) -> SpawnResponse:
    try:
        executor: LocalExecutor | SandboxExecutor
        if request.sandbox_mode:
            executor = SandboxExecutor()
        else:
            executor = LocalExecutor()
        result = executor.execute(request.command, env_vars=request.env_vars)
        return SpawnResponse(exit_code=result.exit_code, output=result.output)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Spawn failed: {exc}") from exc


app.get("/v1/capabilities")(capabilities)
app.post("/v1/spawn")(spawn)

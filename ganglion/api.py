from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from ganglion.execution import LocalExecutor, SandboxExecutor
from ganglion.hardware import read_hardware_profile
from ganglion.metrics import MetricsState
from kernel.config import read_profiled, read_secret
from kernel.observability import configure_logging, get_logger, uptime_seconds
from memory.postgres.client import PostgresClient, PostgresConfig

configure_logging(read_profiled("LOG_LEVEL", read_secret("LONGIN_ENV") or "dev") or "INFO")
logger = get_logger("ganglion.api")
metrics_state = MetricsState()

app = FastAPI()


class SpawnRequest(BaseModel):
    """Účel: Request schema pro spawn endpoint.

    Vstupy/Výstupy: command, sandbox_mode a env_vars.
    Vedlejší efekty: Žádné.
    """
    command: str = Field(min_length=1)
    sandbox_mode: bool = True
    env_vars: Dict[str, str] = Field(default_factory=dict)


class SpawnResponse(BaseModel):
    """Účel: Response schema pro spawn endpoint.

    Vstupy/Výstupy: exit_code a output jako odpověď.
    Vedlejší efekty: Žádné.
    """
    exit_code: int
    output: str


class AuditEntry(BaseModel):
    """Účel: Auditní záznam identity.

    Vstupy/Výstupy: event, version, soul_hash, directives, created_at.
    Vedlejší efekty: Žádné.
    """
    event: str
    version: str
    soul_hash: str
    directives: Dict[str, object]
    created_at: str


class AuditPruneRequest(BaseModel):
    """Účel: Request schema pro prořezávání audit logu.

    Vstupy/Výstupy: older_than_days, keep_latest.
    Vedlejší efekty: Žádné.
    """
    older_than_days: Optional[int] = None
    keep_latest: Optional[int] = None


class AuditPruneResponse(BaseModel):
    """Účel: Response schema pro prořezávání audit logu.

    Vstupy/Výstupy: deleted.
    Vedlejší efekty: Žádné.
    """
    deleted: int


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


def telemetry() -> Dict[str, object]:
    try:
        payload = read_hardware_profile()
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        return payload
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Telemetry failed: {exc}") from exc


def health() -> Dict[str, object]:
    try:
        return {"status": "ok", "uptime_seconds": uptime_seconds()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Health failed: {exc}") from exc


def readiness() -> Dict[str, object]:
    try:
        client = _get_postgres_client()
        ok, error = client.health_check()
        status = "ok" if ok else "degraded"
        return {"status": status, "postgres": {"ok": ok, "error": error}}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Readiness failed: {exc}") from exc


def metrics() -> Dict[str, object]:
    try:
        payload = metrics_state.snapshot()
        payload["service_uptime_seconds"] = uptime_seconds()
        return payload
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Metrics failed: {exc}") from exc


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.monotonic()
    path = request.url.path
    try:
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000.0
        metrics_state.record_request(path, response.status_code, None)
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response
    except Exception as exc:
        duration_ms = (time.monotonic() - start) * 1000.0
        metrics_state.record_request(path, 500, str(exc))
        logger.error(
            f"request_error method={request.method} path={path} duration_ms={round(duration_ms, 2)} error={exc}"
        )
        raise


def _load_postgres_dsn() -> str:
    profile = read_secret("LONGIN_ENV") or "dev"
    dsn = read_profiled("POSTGRES_DSN", profile) or read_profiled("DATABASE_URL", profile)
    if not dsn:
        raise RuntimeError("POSTGRES_DSN is not configured")
    return dsn


def _get_postgres_client() -> PostgresClient:
    try:
        dsn = _load_postgres_dsn()
        return PostgresClient(PostgresConfig(dsn=dsn))
    except Exception as exc:
        raise RuntimeError(f"Postgres config failed: {exc}") from exc


def identity_audit(
    event: Optional[str] = None,
    version: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, object]:
    try:
        client = _get_postgres_client()
        rows = client.search_identity_audit(event=event, version=version, limit=limit)
        return {
            "items": [
                AuditEntry(
                    event=row[0],
                    version=row[1],
                    soul_hash=row[2],
                    directives=dict(row[3]),
                    created_at=str(row[4]),
                ).model_dump()
                for row in rows
            ]
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Identity audit read failed: {exc}") from exc


def identity_audit_prune(request: AuditPruneRequest) -> AuditPruneResponse:
    try:
        client = _get_postgres_client()
        deleted = client.prune_identity_audit(
            older_than_days=request.older_than_days,
            keep_latest=request.keep_latest,
        )
        return AuditPruneResponse(deleted=deleted)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Identity audit prune failed: {exc}") from exc


app.get("/v1/capabilities")(capabilities)
app.post("/v1/spawn")(spawn)
app.get("/v1/telemetry")(telemetry)
app.get("/v1/identity-audit")(identity_audit)
app.post("/v1/identity-audit/prune")(identity_audit_prune)
app.get("/v1/health")(health)
app.get("/v1/ready")(readiness)
app.get("/v1/metrics")(metrics)

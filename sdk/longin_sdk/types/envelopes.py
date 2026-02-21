from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EnvelopeHeaders(BaseModel):
    tags: List[str] = Field(default_factory=list)
    predictive_chain: List[str] = Field(default_factory=list)
    source: Optional[str] = None


class Envelope(BaseModel):
    headers: EnvelopeHeaders
    payload: Dict[str, object]

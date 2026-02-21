from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EnvelopeHeaders(BaseModel):
    """Účel: Struktura hlaviček pro MCP/Redis zprávy.

    Vstupy/Výstupy: tags, predictive_chain a source jako metadata.
    Vedlejší efekty: Žádné.
    """
    tags: List[str] = Field(default_factory=list)
    predictive_chain: List[str] = Field(default_factory=list)
    source: Optional[str] = None


class Envelope(BaseModel):
    """Účel: Obálka zprávy s hlavičkami a payloadem.

    Vstupy/Výstupy: headers a payload jako obsah zprávy.
    Vedlejší efekty: Žádné.
    """
    headers: EnvelopeHeaders
    payload: Dict[str, object]

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List


@dataclass
class SimpleEmbedder:
    """Účel: Generuje deterministické embeddingy z textu.

    Vstupy/Výstupy: Vstupem je text, výstupem seznam float dimenzí.
    Vedlejší efekty: Žádné.
    """
    dimensions: int = 1536

    def embed(self, text: str) -> List[float]:
        try:
            raw = text.encode("utf-8")
        except Exception as exc:
            raise RuntimeError(f"Embed input failed: {exc}") from exc
        digest = hashlib.sha256(raw).digest()
        values: List[float] = []
        while len(values) < self.dimensions:
            for byte in digest:
                values.append((byte / 255.0) * 2.0 - 1.0)
                if len(values) >= self.dimensions:
                    break
            digest = hashlib.sha256(digest).digest()
        return values

# Page-1

## Krok 4: Přidat ego/soul.md a boot proces identity

**Úkol:** Zavést boot identity se soul definicí a perzistencí.

**Změny:**

- kernel/security/identity_boot.py L1-L91: loader identity, hashing a uložení do Redis/Postgres.
- kernel/runtime.py L16-L151: napojení identity bootu při startu runtime.
- ego/soul.md L1-L13: definice identity (WHO AM I, PRIME DIRECTIVES, TONE OF VOICE).
- tests/test_identity_boot.py L1-L38: test perzistence direktiv a verze identity.

## Krok 5: Doplnit integrační a safety testy

**Úkol:** Doplnit integrační a bezpečnostní testy.

**Změny:**

- tests/test_kernel_runtime.py L6-L97: integrační test bootu identity v runtime.
- tests/test_runner.py L1-L56: safety testy SiblingRunneru (blokované importy, timeout, výstup).
- kernel/arbiter/core.py L25-L29: mypy fix pro import psutil.

## Krok 5: Dokumentace

**Úkol:** Aktualizace stavu kroků a mapování implementace.

**Změny:**

- PLAN.md L3-L7: aktualizace stavu kroků 1–5.
- IMPLEMENTATION.md L44-L83: doplnění identity bootu, soul.md, testů a odkazů na deník.

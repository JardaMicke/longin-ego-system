from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from kernel.config import read_profiled, read_secret
from memory.postgres.migrations import MigrationRunner, apply_seed


def _resolve_dsn(profile: str) -> str:
    dsn = read_profiled("POSTGRES_DSN", profile) or read_profiled("DATABASE_URL", profile)
    if not dsn:
        raise RuntimeError("POSTGRES_DSN is not configured")
    return dsn


def _resolve_profile(profile: Optional[str]) -> str:
    return profile or read_secret("LONGIN_ENV") or "dev"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    parser.add_argument("--migrations-dir", default="migrations")
    parser.add_argument("--seed", default=None, choices=[None, "test", "prod"])
    parser.add_argument("--seed-dir", default="seeds")
    args = parser.parse_args(argv)
    profile = _resolve_profile(args.profile)
    dsn = _resolve_dsn(profile)
    migrations_dir = Path(args.migrations_dir)
    runner = MigrationRunner(dsn, migrations_dir)
    runner.apply_all()
    if args.seed:
        seed_path = Path(args.seed_dir) / f"{args.seed}.sql"
        apply_seed(dsn, seed_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

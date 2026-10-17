"""Tests never talk to Supabase: env vars point to a dummy project and every test
patches the client it needs. Set before any app import so .env values are ignored."""
import base64
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.test"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402


def make_jwt(claims: dict) -> str:
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
    return f"{enc({'alg': 'none'})}.{enc(claims)}.sig"


class FakeTable:
    """Minimal stand-in for supabase.table(...): applies eq() filters to in-memory rows."""

    def __init__(self, rows: list[dict]):
        self.rows, self.filters, self.single = rows, {}, False

    def select(self, *_a, **_k): return self
    def order(self, *_a, **_k): return self
    def limit(self, *_a, **_k): return self
    def eq(self, col, val): self.filters[col] = val; return self
    def maybe_single(self): self.single = True; return self

    def execute(self):
        hits = [r for r in self.rows if all(r.get(k) == v for k, v in self.filters.items())]
        if self.single:  # postgrest returns None (not an empty response) when nothing matches
            return SimpleNamespace(data=hits[0]) if hits else None
        return SimpleNamespace(data=hits)


@pytest.fixture
def fake_db():
    """Dict of table name -> rows; returns an object usable in place of `supabase`."""
    tables: dict[str, list[dict]] = {}
    client = SimpleNamespace(table=lambda name: FakeTable(tables.setdefault(name, [])))
    return tables, client

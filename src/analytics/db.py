"""DuckDB in-memory wrapper over Parquet views — Interpret stage support."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "sample"
_DEFAULT_PARQUET = _DATA_DIR / "formations.parquet"


def _ensure_seed(parquet_path: Path) -> None:
    """Generate the seed Parquet on first use — mirrors "served at load"."""
    if parquet_path.exists():
        return
    from src.ingest.loader import load_and_write_parquet

    load_and_write_parquet(output_dir=parquet_path.parent)


def connect(parquet_glob: Path | str | None = None) -> duckdb.DuckDBPyConnection:
    """Open an in-memory DuckDB connection and register Parquet as a view."""
    parquet_path = Path(parquet_glob) if parquet_glob else _DEFAULT_PARQUET
    _ensure_seed(parquet_path)
    con = duckdb.connect(database=":memory:")
    escaped_path = str(parquet_path).replace("'", "''")
    con.execute(f"CREATE OR REPLACE VIEW formations AS SELECT * FROM read_parquet('{escaped_path}')")
    return con


def query(sql: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
    """Run vectorized SQL; return rows as dicts. Never let the LLM invent numbers."""
    con = connect()
    try:
        cursor = con.execute(sql, params) if params is not None else con.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        con.close()

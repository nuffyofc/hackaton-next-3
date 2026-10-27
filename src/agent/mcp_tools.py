"""MCP / tool bindings for DuckDB analytics — Extension point #3."""
from __future__ import annotations

from typing import Any


def run_metrics_tool(query_id: str) -> dict[str, Any]:
    """Expose metrics.compute_facts as a type-safe tool for the Foundry agent."""
    raise NotImplementedError("Fill src/agent/mcp_tools.py after choosing a domain")


def list_tools() -> list[dict[str, Any]]:
    """Return tool schemas (see prompts/tool_definitions.json)."""
    raise NotImplementedError("Fill src/agent/mcp_tools.py after choosing a domain")

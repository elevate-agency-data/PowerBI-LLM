"""stdio MCP client wrapper for the Power BI Modeling MCP Server.

Reads `MCP_SERVER_EXE` from the environment (loaded from .env at module level).
A sidebar override is supported by passing `exe_override` to `get_server_params`.
"""

from __future__ import annotations

import asyncio
import os
import threading
from pathlib import Path
from typing import Any, Coroutine

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run an async coroutine to completion regardless of caller context.

    Streamlit's main thread already owns an event loop, so a naive `asyncio.run`
    raises "asyncio.run() cannot be called from a running event loop". We always
    execute on a dedicated thread with its own fresh loop, which keeps callers
    sync-friendly while letting us own the loop lifecycle for stdio_client.
    """
    container: dict[str, Any] = {}

    def runner() -> None:
        try:
            container["value"] = asyncio.run(coro)
        except BaseException as exc:  # propagate to caller thread
            container["error"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in container:
        raise container["error"]
    return container["value"]

# Suppress server stderr (CREATE_NO_WINDOW pipe avoidance on Windows).
_DEVNULL = open(os.devnull, "w")

# Generous timeout for first run: .NET single-file app extracts itself (~60s).
INIT_TIMEOUT = 120
TOOL_TIMEOUT = 60


def resolve_exe_path(exe_override: str | None = None) -> str:
    """Return the resolved MCP_SERVER_EXE path. Raises on missing/invalid path."""
    exe_path = (exe_override or os.getenv("MCP_SERVER_EXE", "")).strip()
    if not exe_path:
        raise RuntimeError(
            "MCP_SERVER_EXE is not set. Provide it via .env or the sidebar override."
        )
    if not Path(exe_path).exists():
        raise RuntimeError(
            f"Power BI MCP Server executable not found at:\n  {exe_path}\n\n"
            "Download from https://github.com/microsoft/powerbi-modeling-mcp and "
            "update MCP_SERVER_EXE."
        )
    return exe_path


def get_server_params(exe_override: str | None = None) -> StdioServerParameters:
    """Build StdioServerParameters for the MCP server binary."""
    exe_path = resolve_exe_path(exe_override)
    return StdioServerParameters(
        command=exe_path,
        args=["--start"],
        env=dict(os.environ),
        encoding_error_handler="replace",
    )


# ── Public synchronous API ────────────────────────────────────────────────────

def list_available_tools(exe_override: str | None = None) -> list[dict]:
    """Return tool definitions from the MCP server (used to build the schema)."""
    return run_async(_list_tools_async(exe_override))


# ── Session-level tool call (async — called inside an open session) ───────────

async def call_tool_in_session(
    session: ClientSession, tool_name: str, arguments: dict
) -> str:
    """Call a tool inside an already-open MCP session. Returns result as string."""
    try:
        async with asyncio.timeout(TOOL_TIMEOUT):
            result = await session.call_tool(tool_name, arguments=arguments)
            return _extract_result_text(result)
    except TimeoutError:
        return f"ERROR: Tool '{tool_name}' timed out after {TOOL_TIMEOUT}s."
    except Exception as exc:
        return f"ERROR calling tool '{tool_name}': {exc}"


# ── Internal async helpers ────────────────────────────────────────────────────

async def _list_tools_async(exe_override: str | None) -> list[dict]:
    server_params = get_server_params(exe_override)
    try:
        async with asyncio.timeout(INIT_TIMEOUT):
            async with stdio_client(server_params, errlog=_DEVNULL) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.list_tools()
                    return [
                        {
                            "name": t.name,
                            "description": t.description or "",
                            "input_schema": t.inputSchema,
                        }
                        for t in result.tools
                    ]
    except TimeoutError:
        raise RuntimeError(
            f"MCP Server did not respond within {INIT_TIMEOUT}s.\n"
            "On first run, the server extracts itself (~60s). Try again in a moment."
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to connect to Power BI MCP Server: {exc}") from exc


def _extract_result_text(result) -> str:
    if result is None:
        return ""
    content = getattr(result, "content", None)
    if content is None:
        return str(result)
    if isinstance(content, list):
        parts = []
        for item in content:
            text = getattr(item, "text", None)
            parts.append(text if text is not None else str(item))
        return "\n".join(parts)
    return str(content)

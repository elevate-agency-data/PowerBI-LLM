"""Claude ↔ MCP tool-use loop for the chat tab.

Opens ONE MCP session per `run_agent()` call so connection state persists across
all tool invocations Claude issues. Tightened cost controls vs. the demo:

- MAX_ITERATIONS = 6
- max_tokens default = 4096
- read-oriented tool schema only (connection_operations is hidden from Claude)
- tool schema is cached in-process after first list_tools call
"""

from __future__ import annotations

import asyncio
import threading
from typing import Optional

import anthropic
from mcp import ClientSession
from mcp.client.stdio import stdio_client

import config.config as config
from src.mcp_connecter import mcp_client  # noqa: F401  (used as namespace alias)
from src.mcp_connecter.fabric_connection import FabricCredentials, connect


MAX_ITERATIONS = 6
DEFAULT_MAX_TOKENS = 4096

# Tools exposed to Claude — read-only essentials only. `connection_operations`
# is intentionally hidden because the Python layer handles connection lifecycle.
EXPOSED_TOOLS = {
    "model_operations",
    "table_operations",
    "column_operations",
    "measure_operations",
    "relationship_operations",
    "dax_query_operations",
    "security_role_operations",
}


# Module-level cache for the tool schema (keyed by exe override).
_tools_cache: dict[str, list[dict]] = {}
_tools_cache_lock = threading.Lock()


def get_tools_schema(exe_override: Optional[str] = None) -> list[dict]:
    """Fetch (or return cached) Anthropic tool schema from the MCP server."""
    cache_key = exe_override or ""
    with _tools_cache_lock:
        cached = _tools_cache.get(cache_key)
        if cached is not None:
            return cached

    raw_tools = mcp_client.list_available_tools(exe_override)
    schema = [
        {
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": tool["input_schema"],
        }
        for tool in raw_tools
        if tool["name"] in EXPOSED_TOOLS
    ]
    with _tools_cache_lock:
        _tools_cache[cache_key] = schema
    return schema


def reset_tools_cache() -> None:
    with _tools_cache_lock:
        _tools_cache.clear()


def run_agent(
    *,
    api_key: str,
    system_prompt: str,
    user_message: str,
    credentials: FabricCredentials,
    message_history: Optional[list[dict]] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    exe_override: Optional[str] = None,
) -> dict:
    """Run the Claude tool-use loop against the Power BI MCP Server.

    Returns:
        {
            "final_answer": str,
            "tool_calls": [{"tool": str, "input": dict, "output": str}, ...],
            "messages": list[dict],  # full updated message history
        }
    """
    # Fetch the tools schema synchronously BEFORE entering the agent loop so the
    # async impl can rely on a ready schema and no nested loop creation.
    tools_schema = get_tools_schema(exe_override)
    return mcp_client.run_async(
        _run_agent_async(
            api_key=api_key,
            system_prompt=system_prompt,
            user_message=user_message,
            credentials=credentials,
            message_history=message_history,
            max_tokens=max_tokens,
            exe_override=exe_override,
            tools_schema=tools_schema,
        )
    )


# ── Internal async impl ───────────────────────────────────────────────────────

async def _run_agent_async(
    *,
    api_key: str,
    system_prompt: str,
    user_message: str,
    credentials: FabricCredentials,
    message_history: Optional[list[dict]],
    max_tokens: int,
    exe_override: Optional[str],
    tools_schema: list[dict],
) -> dict:
    server_params = mcp_client.get_server_params(exe_override)

    try:
        async with stdio_client(server_params, errlog=mcp_client._DEVNULL) as (
            read,
            write,
        ):
            async with ClientSession(read, write) as session:
                try:
                    async with asyncio.timeout(mcp_client.INIT_TIMEOUT):
                        await session.initialize()
                except TimeoutError:
                    raise RuntimeError(
                        f"MCP Server did not respond within {mcp_client.INIT_TIMEOUT}s."
                    )

                conn_error = await connect(session, credentials)
                if conn_error:
                    return {
                        "final_answer": f"**Connection Error**\n\n{conn_error}",
                        "tool_calls": [],
                        "messages": message_history or [],
                    }

                return await _tool_use_loop(
                    session=session,
                    api_key=api_key,
                    system_prompt=system_prompt,
                    user_message=user_message,
                    tools_schema=tools_schema,
                    message_history=message_history,
                    max_tokens=max_tokens,
                )
    except RuntimeError:
        raise
    except Exception as exc:
        # anyio wraps background-task exceptions in ExceptionGroup — unwrap.
        if hasattr(exc, "exceptions") and exc.exceptions:
            cause = exc.exceptions[0]
            if hasattr(cause, "exceptions") and cause.exceptions:
                cause = cause.exceptions[0]
            raise RuntimeError(str(cause)) from cause
        raise RuntimeError(str(exc)) from exc


async def _tool_use_loop(
    *,
    session: ClientSession,
    api_key: str,
    system_prompt: str,
    user_message: str,
    tools_schema: list[dict],
    message_history: Optional[list[dict]],
    max_tokens: int,
) -> dict:
    client = anthropic.Anthropic(api_key=api_key)

    if message_history:
        messages = list(message_history)
        messages.append({"role": "user", "content": user_message})
    else:
        messages = [{"role": "user", "content": user_message}]

    tool_calls_log: list[dict] = []
    final_answer = ""
    iteration = 0

    while iteration < MAX_ITERATIONS:
        response = await asyncio.to_thread(
            client.messages.create,
            model=config.DEFAULT_CHAT_MODEL,
            system=system_prompt,
            messages=messages,
            tools=tools_schema,
            max_tokens=max_tokens,
        )

        if response.stop_reason == "end_turn":
            final_answer = _extract_text(response.content)
            messages.append({"role": "assistant", "content": response.content})
            break

        if response.stop_reason == "tool_use":
            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in tool_use_blocks:
                result_str = await mcp_client.call_tool_in_session(
                    session, block.name, block.input
                )
                tool_calls_log.append(
                    {"tool": block.name, "input": block.input, "output": result_str}
                )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    }
                )

            messages.append({"role": "user", "content": tool_results})
            iteration += 1
            continue

        # Unexpected stop reason — surface what we have.
        final_answer = (
            _extract_text(response.content) or f"[Stopped: {response.stop_reason}]"
        )
        messages.append({"role": "assistant", "content": response.content})
        break

    if iteration >= MAX_ITERATIONS:
        final_answer = (
            (final_answer or "")
            + "\n\n[Reached maximum tool call iterations.]"
        )

    return {
        "final_answer": final_answer,
        "tool_calls": tool_calls_log,
        "messages": messages,
    }


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            b.text
            for b in content
            if hasattr(b, "text") and getattr(b, "type", "") == "text"
        ]
        return "\n".join(parts)
    return str(content)

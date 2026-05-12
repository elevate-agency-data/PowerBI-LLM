"""Build Fabric XMLA connection strings and call `connection_operations`.

Supported auth modes (UI-exposed):
  - interactive: server prompts Microsoft auth in a browser, no creds embedded.
  - username+password: credentials embedded directly in the connection string.

Service-principal flow is intentionally NOT exposed in the unified UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mcp import ClientSession

from src.mcp_connecter import mcp_client


@dataclass
class FabricCredentials:
    xmla_endpoint: str
    auth_mode: str  # "interactive" | "username+password"
    username: Optional[str] = None
    password: Optional[str] = None
    initial_catalog: Optional[str] = None


def build_connection_string(creds: FabricCredentials) -> str:
    """Assemble the OLE DB connection string for the chosen auth mode."""
    endpoint = creds.xmla_endpoint.strip()
    if creds.auth_mode == "interactive":
        connection_string = f"Data Source={endpoint};"
    elif creds.auth_mode == "username+password":
        if not creds.username or not creds.password:
            raise ValueError(
                "Username and password are required for username+password auth."
            )
        connection_string = (
            f"Data Source={endpoint};"
            f"User ID={creds.username};Password={creds.password};"
        )
    else:
        raise ValueError(
            f"Unsupported auth mode: '{creds.auth_mode}'. "
            "Use 'interactive' or 'username+password'."
        )

    if creds.initial_catalog:
        connection_string += f"Initial Catalog={creds.initial_catalog};"
    return connection_string


async def connect(session: ClientSession, creds: FabricCredentials) -> Optional[str]:
    """Call `connection_operations` to connect via XMLA.

    Returns an error string on failure, None on success.
    """
    try:
        connection_string = build_connection_string(creds)
    except ValueError as exc:
        return str(exc)

    result = await mcp_client.call_tool_in_session(
        session,
        "connection_operations",
        {"request": {"operation": "Connect", "connectionString": connection_string}},
    )

    if result.startswith("ERROR") or '"success":false' in result:
        return (
            f"Failed to connect to Fabric XMLA endpoint.\n\n"
            f"Endpoint: {creds.xmla_endpoint}\nAuth mode: {creds.auth_mode}\n\n"
            f"Details: {result}\n\n"
            "Check: workspace is on Fabric capacity, and XMLA read/write is "
            "enabled in the Power BI tenant admin portal."
        )
    return None

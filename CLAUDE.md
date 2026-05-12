# CLAUDE.md

Project-specific instructions for Claude Code when working on **PowerBI-LLM**.

## Project Overview

PowerBI-LLM is a Streamlit app with three tabs:

- **Documentation** — parses a PBIP zip → Markdown documentation (Claude Sonnet 4.6)
- **README** — injects a README page into the PBIP report.json (Claude Sonnet 4.6)
- **Chat** — interactive Q&A on a live Fabric semantic model via the Power BI
  Modeling MCP Server (Claude Haiku 4.5 in a tool-use loop)

Entry point: [streamlit_app.py](streamlit_app.py)
Architecture details: see [README.md](README.md)

## Development Rules

### SOLID — Single Responsibility & Open/Closed (mandatory)

All contributors (human and AI) MUST respect the **S** and **O** of SOLID when
writing or modifying code in this project:

- **S — Single Responsibility Principle**: every module, class, and function
  must have one and only one reason to change. Do not mix concerns (e.g., do
  not put file I/O, Anthropic calls, and UI logic in the same function).
  - UI code → [src/ui/](src/ui/) and [streamlit_app.py](streamlit_app.py)
  - Business orchestration → [src/handlers/](src/handlers/)
  - Anthropic LLM calls → [src/anthropic_connecter/](src/anthropic_connecter/)
  - MCP integration (stdio client, Fabric, tool-use loop) →
    [src/mcp_connecter/](src/mcp_connecter/)
  - File/JSON parsing → [src/file_operator/](src/file_operator/) and
    [src/json_operator/](src/json_operator/)
  - Validation → [src/validators/](src/validators/)

- **O — Open/Closed Principle**: modules must be open for extension but closed
  for modification. When adding a new tab capability, **extend** existing
  abstractions rather than editing stable code paths.
  - New tab features MUST implement the `TabHandler` interface in
    [src/anthropic_connecter/handlers/base_handler.py](src/anthropic_connecter/handlers/base_handler.py)
    and be invoked from a dedicated handler in `src/handlers/` — do NOT add
    `if/elif` branches inside existing handlers for new tab variants.
  - Prefer composition, polymorphism, and dependency injection over modifying
    existing handlers.

When a change appears to require violating S or O, stop and propose a refactor
instead.

## Locked decisions

These choices have been made already; do not relitigate them in routine PRs:

- LLM provider is **Anthropic only**. No OpenAI code path.
- Docs/README use Claude Sonnet 4.6 (`claude-sonnet-4-6`). Chat uses Claude
  Haiku 4.5 (`claude-haiku-4-5-20251001`). Model IDs live in
  [config/config.py](config/config.py). No model dropdown in the UI.
- Chat tab connects to **Fabric XMLA** only — interactive or username+password
  auth. No local Power BI Desktop path, no service principal in the UI.
- Chat tool-use loop is capped at `MAX_ITERATIONS = 6` and
  `max_tokens = 4096`. Only the seven read-only MCP tools are exposed to
  Claude. The tools schema is cached in-process.
- Chat history is session-only; no disk persistence.
- Secrets (Anthropic key, Fabric credentials) are entered in the sidebar at
  runtime. Only `MCP_SERVER_EXE` lives in `.env`.

## Useful entry points

| Concern | File |
|---------|------|
| Streamlit tab wiring | [streamlit_app.py](streamlit_app.py) |
| Sidebar inputs | [src/ui/sidebar.py](src/ui/sidebar.py) |
| Chat UI | [src/ui/tab_chat.py](src/ui/tab_chat.py) |
| TabHandler abstraction | [src/anthropic_connecter/handlers/base_handler.py](src/anthropic_connecter/handlers/base_handler.py) |
| Claude API wrappers | [src/anthropic_connecter/general_anthropic_connecter.py](src/anthropic_connecter/general_anthropic_connecter.py) |
| MCP stdio client | [src/mcp_connecter/mcp_client.py](src/mcp_connecter/mcp_client.py) |
| Tool-use loop | [src/mcp_connecter/claude_agent.py](src/mcp_connecter/claude_agent.py) |
| Fabric connection string | [src/mcp_connecter/fabric_connection.py](src/mcp_connecter/fabric_connection.py) |

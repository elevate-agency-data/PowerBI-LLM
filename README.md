# PowerBI-LLM

> Unified Power BI documentation + live chat assistant, powered by Claude.

## Overview

**PowerBI-LLM** is a Streamlit application that turns Power BI work into three
focused experiences:

1. **Documentation** — parses a PBIP zip and produces a complete Markdown
   documentation file (powered by Claude Sonnet 4.6).
2. **README** — generates a README page embedded directly inside a Power BI
   report using the PBIP zip and a PDF export, then repackages the modified
   PBIP for download (Claude Sonnet 4.6).
3. **Chat** — interactive Q&A against a live Fabric semantic model via the
   [Microsoft Power BI Modeling MCP Server](https://github.com/microsoft/powerbi-modeling-mcp),
   driven by Claude Haiku 4.5 in a tool-use loop.

The app supports English, French, and Chinese output across every tab.

---

## Architecture

```
┌──────────────────────── Streamlit UI ────────────────────────┐
│  streamlit_app.py     ┃  src/ui/sidebar.py                   │
│  tabs: Documentation  ┃  src/ui/tab_chat.py                  │
│         README         ┃                                      │
│         Chat           ┃                                      │
└────────┬──────────────────────────────────────────┬──────────┘
         │ Documentation / README                   │ Chat
         ▼                                          ▼
┌─────────────────────────┐         ┌────────────────────────────┐
│ src/handlers/           │         │ src/mcp_connecter/         │
│  documentation_handler  │         │  mcp_client.py             │
│  readme_handler         │         │  fabric_connection.py      │
└────────┬────────────────┘         │  claude_agent.py           │
         │                          │  prompts.py                │
         ▼                          └─────────┬──────────────────┘
┌─────────────────────────┐                   │ stdio
│ src/anthropic_connecter │                   ▼
│  TabHandler abstraction │         ┌────────────────────────────┐
│  Sonnet 4.6 LLM calls   │         │ Power BI MCP Server (.exe) │
└────────┬────────────────┘         │ (Fabric XMLA endpoint)     │
         │                          └────────────────────────────┘
         ▼
┌─────────────────────────┐
│ src/json_operator       │
│ src/file_operator       │
└─────────────────────────┘
```

### Layer responsibilities

| Layer | Path | Role |
|-------|------|------|
| UI | `streamlit_app.py`, `src/ui/` | Tabs, sidebar, file uploads, chat widget |
| Documentation / README orchestration | `src/handlers/` | Flow control for the two doc tabs |
| Claude API | `src/anthropic_connecter/` | LLM wrappers + `TabHandler` abstraction |
| MCP integration | `src/mcp_connecter/` | stdio client, Fabric connect, tool-use loop |
| Parsing | `src/json_operator/`, `src/file_operator/` | PBIP zip + report.json + PDF |
| Validation | `src/validators/` | Per-tab input validation |
| Config | `config/` | Constants, translations |

### Cost-control notes

The MCP tool calls return potentially large XMLA payloads, so the Chat tab is
tuned to keep token usage in check:

- `MAX_ITERATIONS = 6` and `max_tokens = 4096` for chat.
- Only seven **read-only** MCP tools (`model_operations`, `table_operations`,
  `column_operations`, `measure_operations`, `relationship_operations`,
  `dax_query_operations`, `security_role_operations`) are exposed to Claude.
- `connection_operations` is handled in Python and hidden from Claude.
- The MCP tools schema is cached in-process after the first `list_tools` call.

---

## Setup

### Prerequisites

- Python 3.11+ (tested with 3.14)
- Anthropic API key (`sk-ant-…`)
- A Power BI Project as a `.zip` (PBIP format) and, for README only, a PDF
  export of the report
- For Chat: a Fabric capacity workspace with XMLA read/write enabled, plus the
  Microsoft Power BI Modeling MCP Server binary

### Install

```powershell
pip install -r requirements.txt
```

### Configure the MCP binary (Chat tab only)

1. Download and extract the VSIX from
   <https://github.com/microsoft/powerbi-modeling-mcp>.
2. Locate `extension/server/powerbi-modeling-mcp.exe`.
3. Create a `.env` file at the repo root:

   ```env
   MCP_SERVER_EXE=C:\path\to\extension\server\powerbi-modeling-mcp.exe
   ```

   See `.env.example`. `.env` is gitignored. You can also override the path in
   the sidebar "Chat connection" panel.

### Fabric XMLA auth

The Chat tab supports two auth modes (selected in the sidebar):

- **interactive** — recommended. The MCP server handles Microsoft sign-in via
  the browser and reuses cached refresh tokens.
- **username+password** — embeds credentials directly in the XMLA connection
  string. Best for headless scenarios; not compatible with workspaces that
  already have a cached interactive token until that cache expires.

Service principal is not exposed in the UI.

---

## Running

```powershell
streamlit run streamlit_app.py
```

In the sidebar:

1. Paste your **Anthropic API key**.
2. Pick output language (EN/FR/ZH).
3. Upload the **PBIP `.zip`** (and **PDF** if you'll use the README tab).
4. For Chat: open **Chat connection**, fill in the XMLA endpoint and auth.

Then pick a tab and run the action. Output:

- **Documentation** — Markdown file (`.md`) download + in-app preview.
- **README** — modified PBIP zip ready to re-open in Power BI Desktop.
- **Chat** — interactive multi-turn conversation against the live model. Chat
  history lives only in the Streamlit session.

---

## Development rules

Read [`CLAUDE.md`](CLAUDE.md) before contributing. The short version:

- **SOLID — S & O are mandatory**: every module has one reason to change, and
  new capabilities **extend** abstractions rather than modifying stable code.
- New tab features implement `TabHandler` in
  `src/anthropic_connecter/handlers/base_handler.py`. Do **not** add `if/elif`
  branches in callers.
- The folder boundaries above are load-bearing: UI in `src/ui/`, orchestration
  in `src/handlers/`, LLM calls in `src/anthropic_connecter/`, MCP in
  `src/mcp_connecter/`, parsing in `src/json_operator/` and `src/file_operator/`,
  validation in `src/validators/`.

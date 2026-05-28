"""Chat tab: interactive Q&A against the live Power BI model via MCP."""

from __future__ import annotations

import streamlit as st

from config.translation import t
from src.mcp_connecter import claude_agent
from src.mcp_connecter.fabric_connection import FabricCredentials
from src.mcp_connecter.prompts import chat_system_prompt
from src.ui.components import empty_state, section_header
from src.validators.input_validator import validate_chat_inputs


def render(sidebar_values) -> None:
    section_header(
        eyebrow="Live dataset chat",
        title="Chat with your Power BI model",
        subtitle=(
            "Ask anything about the dataset — Claude queries the live Fabric "
            "semantic model via MCP instead of guessing."
        ),
    )

    is_valid, message = validate_chat_inputs(
        sidebar_values.anthropic_api_key,
        sidebar_values.xmla_endpoint,
        sidebar_values.auth_mode,
        sidebar_values.username,
        sidebar_values.password,
    )
    if not is_valid:
        st.warning(message, icon="⚠")
        return

    _ensure_chat_state()

    if st.session_state.chat_history:
        if st.button("Clear chat"):
            st.session_state.chat_history = []
            st.session_state.chat_tool_calls = {}
            st.rerun()
    else:
        empty_state(
            title="Ready to chat",
            body=(
                "Try asking <em>“List the tables in the model”</em> or "
                "<em>“What measures are defined?”</em>"
            ),
        )

    _render_history()

    user_input = st.chat_input("Ask anything about your Power BI model...")
    if not user_input:
        return

    with st.chat_message("user"):
        st.markdown(user_input)

    credentials = FabricCredentials(
        xmla_endpoint=sidebar_values.xmla_endpoint,
        auth_mode=sidebar_values.auth_mode,
        username=sidebar_values.username or None,
        password=sidebar_values.password or None,
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = claude_agent.run_agent(
                    api_key=sidebar_values.anthropic_api_key,
                    system_prompt=chat_system_prompt(sidebar_values.language),
                    user_message=user_input,
                    credentials=credentials,
                    message_history=st.session_state.chat_history,
                    exe_override=sidebar_values.mcp_exe_override or None,
                )
            except RuntimeError as exc:
                st.error(str(exc))
                return

        st.markdown(result["final_answer"])
        if result["tool_calls"]:
            _render_tool_calls(result["tool_calls"])

    new_history = result["messages"]
    st.session_state.chat_history = new_history
    if result["tool_calls"]:
        st.session_state.chat_tool_calls[len(new_history) - 1] = result["tool_calls"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ensure_chat_state() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_tool_calls" not in st.session_state:
        st.session_state.chat_tool_calls = {}


def _render_history() -> None:
    for i, msg in enumerate(st.session_state.chat_history):
        role = msg["role"]
        content = msg["content"]

        if isinstance(content, list):
            # Skip pure tool_result user turns
            if role == "user" and all(
                getattr(b, "type", "") == "tool_result"
                for b in content
                if hasattr(b, "type")
            ):
                continue
            text_parts = [
                getattr(b, "text", "") for b in content if getattr(b, "type", "") == "text"
            ]
            display_text = "\n".join(t for t in text_parts if t)
        else:
            display_text = str(content)

        with st.chat_message(role):
            if display_text:
                st.markdown(display_text)
            if role == "assistant" and i in st.session_state.chat_tool_calls:
                _render_tool_calls(st.session_state.chat_tool_calls[i])


def _render_tool_calls(tool_calls: list[dict]) -> None:
    with st.expander(f"Tool calls ({len(tool_calls)})", expanded=False):
        for call in tool_calls:
            st.markdown(f"**{call['tool']}**")
            st.json(call.get("input", {}))
            output = call.get("output", "")
            if len(output) > 2000:
                output = output[:2000] + "…"
            st.code(output, language="json")

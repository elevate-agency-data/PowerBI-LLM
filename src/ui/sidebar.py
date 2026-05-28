"""Sidebar widgets: API key, language, file uploads, and chat connection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

import config.config as config
from src.ui.components import sidebar_brand, sidebar_section


load_dotenv()


@dataclass
class SidebarValues:
    anthropic_api_key: str
    language: str
    zip_file: object
    pdf_file: object
    xmla_endpoint: str
    auth_mode: str  # "interactive" | "username+password"
    username: str
    password: str
    mcp_exe_override: str


def render_sidebar() -> SidebarValues:
    """Render sidebar widgets and return collected values."""
    sidebar_brand()

    sidebar_section("Credentials", icon="🔑")
    api_key = st.sidebar.text_input(
        config.API_KEY_LABEL,
        type="password",
        placeholder="sk-ant-…",
        help="Your key never leaves this browser session.",
    )

    sidebar_section("Preferences", icon="🌐")
    language_options = ["English", "French", "Chinese"]
    default_idx = (
        language_options.index(config.DEFAULT_LANGUAGE)
        if config.DEFAULT_LANGUAGE in language_options
        else 0
    )
    language = st.sidebar.selectbox("Output language", language_options, index=default_idx)

    sidebar_section("Files", icon="📁")
    zip_file = st.sidebar.file_uploader(
        config.FILE_UPLOAD_LABEL,
        type=["zip"],
        help="Required for Documentation and README tabs.",
    )
    pdf_file = st.sidebar.file_uploader(
        config.FILE_UPLOAD_LABEL_PDF,
        type=["pdf"],
        help="Required only for the README tab.",
    )

    sidebar_section("Chat connection", icon="🔌")
    with st.sidebar.expander("Fabric XMLA settings", expanded=False):
        st.caption(
            "Used only by the Chat tab. Requires a Fabric capacity workspace "
            "with XMLA read enabled."
        )
        xmla_endpoint = st.text_input(
            "Fabric XMLA endpoint",
            placeholder="powerbi://api.fabric.microsoft.com/v1.0/myorg/{workspace}",
        )
        auth_mode = st.radio(
            "Auth mode",
            options=["interactive", "username+password"],
            index=0,
            horizontal=True,
        )
        if auth_mode == "username+password":
            username = st.text_input("Username (UPN)")
            password = st.text_input("Password", type="password")
        else:
            username = ""
            password = ""
        mcp_exe_override = st.text_input(
            "MCP server executable (override)",
            value="",
            placeholder=os.getenv("MCP_SERVER_EXE", "(reads MCP_SERVER_EXE from .env)"),
            help="Leave blank to use MCP_SERVER_EXE from .env.",
        )

    return SidebarValues(
        anthropic_api_key=api_key,
        language=language,
        zip_file=zip_file,
        pdf_file=pdf_file,
        xmla_endpoint=xmla_endpoint.strip(),
        auth_mode=auth_mode,
        username=username,
        password=password,
        mcp_exe_override=mcp_exe_override.strip(),
    )

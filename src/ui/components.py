"""Reusable presentational components for the PowerBI Assistant UI.

Each function emits self-contained HTML that targets the classes defined in
``theme.py``. Components hold no business logic — they only render markup.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


def hero() -> None:
    """Top hero banner shown above the tab strip."""
    st.markdown(
        """
        <div class="pbi-hero">
            <div class="pbi-hero-eyebrow">Power BI Assistant</div>
            <h1 class="pbi-hero-title">Document and explore your Power BI models</h1>
            <p class="pbi-hero-subtitle">
                Generate publish-ready README pages, full Markdown documentation,
                and chat with your live Fabric semantic model — all from your PBIP file.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_cards() -> None:
    """Three feature cards summarising what the app can do."""
    st.markdown(
        """
        <div class="pbi-feature-row">
            <div class="pbi-feature">
                <div class="pbi-feature-icon">📘</div>
                <p class="pbi-feature-title">README page</p>
                <p class="pbi-feature-body">
                    Embedded summary inside the PBIP: objectives, page overview,
                    and per-page KPIs.
                </p>
            </div>
            <div class="pbi-feature">
                <div class="pbi-feature-icon">📄</div>
                <p class="pbi-feature-title">Detailed documentation</p>
                <p class="pbi-feature-body">
                    Complete Markdown reference: tables, measures, and DAX details
                    for every column.
                </p>
            </div>
            <div class="pbi-feature">
                <div class="pbi-feature-icon">💬</div>
                <p class="pbi-feature-title">Chat with your model</p>
                <p class="pbi-feature-body">
                    Ask questions against the live Fabric semantic model via MCP —
                    grounded in real data.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prereqs_strip(api_key: str, zip_file, pdf_file) -> None:
    """At-a-glance pills indicating which inputs are configured."""
    items = [
        ("Anthropic key", bool(api_key and api_key.startswith("sk-"))),
        ("PBIP zip", zip_file is not None),
        ("PDF export", pdf_file is not None),
    ]
    pills = "".join(
        f'<span class="pbi-pill {"ok" if ok else "miss"}">'
        f'<span class="pbi-pill-dot"></span>{label}</span>'
        for label, ok in items
    )
    st.markdown(
        f"""
        <div class="pbi-prereq-wrap">
            <span class="pbi-prereq-label">Inputs</span>
            {pills}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(eyebrow: str, title: str, subtitle: str) -> None:
    """Tab-level header block: eyebrow + title + sub."""
    st.markdown(
        f"""
        <div class="pbi-section-eyebrow">{eyebrow}</div>
        <h2 class="pbi-section-title">{title}</h2>
        <p class="pbi-section-sub">{subtitle}</p>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand(name: str = "Power BI Assistant", tag: str = "Docs · README · Chat") -> None:
    """Branded sidebar header."""
    st.sidebar.markdown(
        f"""
        <div class="pbi-brand">
            <div class="pbi-brand-dot">PB</div>
            <div>
                <div class="pbi-brand-name">{name}</div>
                <div class="pbi-brand-tag">{tag}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_section(label: str, icon: str = "") -> None:
    """Sidebar section divider with an uppercase label."""
    prefix = f"{icon} " if icon else ""
    st.sidebar.markdown(
        f'<div class="pbi-sidebar-section">{prefix}{label}</div>',
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str) -> None:
    """Card shown when a tab has nothing to display yet."""
    st.markdown(
        f"""
        <div class="pbi-empty">
            <div class="pbi-empty-title">{title}</div>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

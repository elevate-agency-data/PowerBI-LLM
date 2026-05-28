"""Streamlit entry point: Documentation | README | Chat."""

import anthropic
import streamlit as st

import config.config as config
from config.translation import t
from src.handlers.documentation_handler import handle_documentation_generation
from src.handlers.readme_handler import handle_readme_generation
from src.ui import tab_chat
from src.ui.components import (
    feature_cards,
    hero,
    prereqs_strip,
    section_header,
)
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme
from src.validators.input_validator import (
    validate_documentation_inputs,
    validate_readme_inputs,
)


def main() -> None:
    apply_theme()
    sidebar_values = render_sidebar()

    hero()
    feature_cards()
    prereqs_strip(
        sidebar_values.anthropic_api_key,
        sidebar_values.zip_file,
        sidebar_values.pdf_file,
    )

    tab_doc, tab_readme, tab_chat_ui = st.tabs(
        ["📄  Documentation", "📘  README", "💬  Chat"]
    )

    with tab_doc:
        _render_documentation_tab(sidebar_values)

    with tab_readme:
        _render_readme_tab(sidebar_values)

    with tab_chat_ui:
        tab_chat.render(sidebar_values)


def _render_documentation_tab(sidebar_values) -> None:
    section_header(
        eyebrow="Detailed documentation",
        title=t(sidebar_values.language, "documentation"),
        subtitle=(
            "Parses the uploaded PBIP zip and produces a complete Markdown "
            "documentation — tables, measures, DAX details, and page descriptions."
        ),
    )

    is_valid, message = validate_documentation_inputs(
        sidebar_values.anthropic_api_key, sidebar_values.zip_file
    )
    if not is_valid:
        st.info(message, icon="ℹ️")
        return

    if st.button(t(sidebar_values.language, "documentation"), key="btn_doc"):
        client = anthropic.Anthropic(api_key=sidebar_values.anthropic_api_key)
        with st.spinner("Generating documentation..."):
            handle_documentation_generation(
                sidebar_values.zip_file,
                sidebar_values.language,
                client,
            )


def _render_readme_tab(sidebar_values) -> None:
    section_header(
        eyebrow="In-report README",
        title=t(sidebar_values.language, "readme"),
        subtitle=(
            "Injects a README page into the PBIP report.json and repackages the "
            "zip for download. Requires the PBIP zip and the PDF export."
        ),
    )

    is_valid, message = validate_readme_inputs(
        sidebar_values.anthropic_api_key,
        sidebar_values.zip_file,
        sidebar_values.pdf_file,
    )
    if not is_valid:
        st.info(message, icon="ℹ️")
        return

    if st.button(t(sidebar_values.language, "readme"), key="btn_readme"):
        client = anthropic.Anthropic(api_key=sidebar_values.anthropic_api_key)
        with st.spinner("Generating README..."):
            handle_readme_generation(
                sidebar_values.zip_file,
                sidebar_values.pdf_file,
                sidebar_values.language,
                client,
            )


if __name__ == "__main__":
    main()

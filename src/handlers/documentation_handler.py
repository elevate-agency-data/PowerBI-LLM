"""Business logic for the Documentation-generation tab."""

import time

import streamlit as st

import config.config as config
from src.file_operator.file_operations import extract_report_and_model
from src.anthropic_connecter.handlers.base_handler import HandlerRequest
from src.anthropic_connecter.handlers.documentation_tab_handler import (
    DocumentationTabHandler,
)


def handle_documentation_generation(zip_file, selected_language, anthropic_client):
    """Generate full Markdown documentation and offer it as a download."""
    start = time.time()
    report_json_content, model_bim_content, *_ = extract_report_and_model(zip_file)

    handler = DocumentationTabHandler()
    try:
        response = handler.process(
            HandlerRequest(
                text="Provide full documentation of the dashboard.",
                report_json_content=report_json_content,
                model_bim_content=model_bim_content,
                report_images=[],
                language=selected_language,
                anthropic_client=anthropic_client,
            )
        )
    except Exception as exc:
        st.error(f"Documentation generation failed: {exc}")
        return

    print(f"Documentation generation took {time.time() - start:.2f}s")
    if "error" in response.message.lower():
        st.error(response.message)
        return
    st.success(response.message)

    if response.file_content:
        st.download_button(
            label=f"Download {config.DOCUMENTATION_FILENAME}",
            data=response.file_content,
            file_name=config.DOCUMENTATION_FILENAME,
            mime="text/markdown",
        )
        with st.expander("Preview", expanded=False):
            st.markdown(response.file_content.decode("utf-8"))

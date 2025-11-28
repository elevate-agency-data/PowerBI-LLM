"""Business logic for the documentation-generation action."""

import time
import streamlit as st
from src.file_operator.file_operations import extract_report_and_model
import config.config as config


def handle_documentation_generation(
    coordinator,
    zip_file,
    selected_language,
    selected_model,
    openai_client,
):
    """Handle documentation generation flow."""
    start = time.time()
    text = "Provide full documentation of the dashboard for confluence."

    report_json_content, model_bim_content, inner_folder_path, report_json_path, _ = (
        extract_report_and_model(zip_file)
    )

    report_images = []
    _, file_content, message = coordinator.process_request(
        text,
        report_json_content,
        model_bim_content,
        report_images,
        selected_language,
        selected_model,
        openai_client,
        requested_function="summary_in_target_platform",
    )
    print(f"Documentation generation took {time.time() - start:.2f}s")
    if "error" in message.lower():
        st.error(message)
        return
    st.success(message)
    if file_content:
        st.download_button(
            label=f"Download {config.DOCUMENTATION_FILENAME}",
            data=file_content,
            file_name=config.DOCUMENTATION_FILENAME,
            mime="text/plain",
        )


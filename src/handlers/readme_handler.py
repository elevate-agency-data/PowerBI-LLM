"""Business logic for the README-generation action."""

import time
import streamlit as st
from src.file_operator.file_operations import (
    extract_report_and_model,
    convert_pdf_to_images,
    write_modified_zip,
)
import config.config as config


def handle_readme_generation(
    coordinator,
    zip_file,
    pdf_file,
    selected_language,
    selected_model,
    openai_client,
):
    """Handle README generation flow."""
    start = time.time()
    text = "Please add a README page to the dashboard."

    report_json_content, model_bim_content, inner_folder_path, report_json_path, _ = (
        extract_report_and_model(zip_file)
    )
    report_images = convert_pdf_to_images(pdf_file)

    modified_json, _, message = coordinator.process_request(
        text,
        report_json_content,
        model_bim_content,
        report_images,
        selected_language,
        selected_model,
        openai_client,
        requested_function="add_read_me",
    )
    print(f"README generation took {time.time() - start:.2f}s")
    if "error" in message.lower():
        st.error(message)
        return
    st.success(message)
    if modified_json:
        modified_zip = write_modified_zip(modified_json, report_json_path, inner_folder_path)
        st.download_button(
            label=f"Download {config.MODIFIED_PBIP_FILENAME}",
            data=modified_zip,
            file_name=config.MODIFIED_PBIP_FILENAME,
            mime="application/zip",
        )


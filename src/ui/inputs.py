"""Main-panel widgets for file uploads and action buttons."""

import streamlit as st
import config.config as config


def render_inputs(selected_language, translate):
    """Render file inputs and action buttons."""
    zip_file = st.file_uploader(config.FILE_UPLOAD_LABEL, type=["zip"])
    pdf_file = st.file_uploader(config.FILE_UPLOAD_LABEL_PDF, type=["pdf"])

    col1, col2 = st.columns(2)
    generate_readme = col1.button(
        translate(selected_language, "readme"),
        disabled=zip_file is None,
        use_container_width=True,
    )
    generate_description = col2.button(
        translate(selected_language, "documentation"),
        disabled=zip_file is None,
        use_container_width=True,
    )

    return zip_file, pdf_file, generate_readme, generate_description


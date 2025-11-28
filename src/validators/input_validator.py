"""Input validation helpers for the Streamlit front-end."""

import config.config as config


def validate_inputs(api_key, zip_file, pdf_file):
    """Validate required inputs and return status + message."""
    if not api_key.startswith("sk-"):
        return False, config.API_KEY_ERROR
    if zip_file is None:
        return False, config.FILE_UPLOAD_ERROR
    if pdf_file is None:
        return False, config.FILE_UPLOAD_ERROR
    return True, ""


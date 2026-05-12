"""Input validation helpers for the Streamlit front-end."""

from typing import Optional, Tuple

import config.config as config


def validate_anthropic_key(api_key: Optional[str]) -> Tuple[bool, str]:
    """Anthropic keys typically start with sk-ant-. Accept any non-empty string."""
    if not api_key:
        return False, config.API_KEY_ERROR
    if not api_key.startswith("sk-"):
        return False, config.API_KEY_ERROR
    return True, ""


def validate_documentation_inputs(api_key, zip_file) -> Tuple[bool, str]:
    """Documentation tab needs the API key and a PBIP zip."""
    ok, msg = validate_anthropic_key(api_key)
    if not ok:
        return ok, msg
    if zip_file is None:
        return False, config.FILE_UPLOAD_ERROR
    return True, ""


def validate_readme_inputs(api_key, zip_file, pdf_file) -> Tuple[bool, str]:
    """README tab needs the API key, the PBIP zip, and a PDF export."""
    ok, msg = validate_anthropic_key(api_key)
    if not ok:
        return ok, msg
    if zip_file is None or pdf_file is None:
        return False, config.FILE_UPLOAD_ERROR
    return True, ""


def validate_chat_inputs(api_key, xmla_endpoint, auth_mode, username, password) -> Tuple[bool, str]:
    """Chat tab requires API key + XMLA endpoint + (interactive | username+password)."""
    ok, msg = validate_anthropic_key(api_key)
    if not ok:
        return ok, msg
    if not xmla_endpoint:
        return False, config.XMLA_CONFIG_ERROR
    if auth_mode == "username+password":
        if not username or not password:
            return False, "Username and password are required for username+password auth."
    return True, ""

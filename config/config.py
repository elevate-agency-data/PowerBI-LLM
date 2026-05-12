"""Configuration constants for the PowerBI Assistant application."""

# Default values
DEFAULT_LANGUAGE = "English"
DEFAULT_PLATFORM = "Confluence"

# Anthropic model IDs (locked — do not expose in the UI).
DEFAULT_DOCS_MODEL = "claude-sonnet-4-6"
DEFAULT_CHAT_MODEL = "claude-haiku-4-5-20251001"

SUPPORTED_TASKS = ["README", "Documentation", "Chat"]

# UI labels
FILE_UPLOAD_LABEL = "Upload the PBIP folder (as a .zip file)"
FILE_UPLOAD_LABEL_PDF = "Upload the PowerBI report (as a .pdf file)"
API_KEY_LABEL = "Anthropic API Key"
REQUEST_LABEL = "Enter your request:"
SUBMIT_BUTTON_LABEL = "Submit"

# File paths and names
DOCUMENTATION_FILENAME = "Documentation.md"
MODIFIED_PBIP_FILENAME = "modified_pbip.zip"

# UI Text
TITLE = "💡Your PowerBI Assistant"

# Error Messages
API_KEY_ERROR = "Please enter your Anthropic API key!"
FILE_UPLOAD_ERROR = "Please upload the PBIP folder as a .zip file and the report PDF."
XMLA_CONFIG_ERROR = (
    "Chat requires an XMLA endpoint and credentials. Fill in the Chat connection panel."
)
UNSUPPORTED_REQUEST_ERROR = (
    "ℹ️ Sorry, your request is beyond my capabilities."
)

# Success Messages
MODIFICATION_SUCCESS = "PBIP folder modified successfully!"

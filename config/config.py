"""Configuration constants for the PowerBI Assistant application."""

# Documentation section titles
DOC_DASHBOARD_OVERVIEW = "h1. Dashboard Overview"
DOC_DETAILED_INFO = "h1. Detailed Information By Page"
DOC_DATASET_INFO = "h1. Dataset Key Information"
DOC_TABLE_SOURCE = "h2. Table Source"
DOC_MEASURES_SUMMARY = "h2. Measures Summary"
DOC_DETAILED_MEASURES = "h2. Detailed Measure Information By Column"

# Default values
DEFAULT_LANGUAGE = "English"
DEFAULT_PLATFORM = "Confluence"
DEFAULT_MODEL = "gpt-5"
SUPPORTED_MODELS = ["gpt-5", "gpt-4.1", "gpt-3.5-turbo"]
SUPPORTED_TASKS = ["README", "Documentation"]
DEFAULT_REQUEST_TEXT = "I want to add a README page to the PowerBI report."

# File paths and names
DOCUMENTATION_FILENAME = "Documentation.txt"
MODIFIED_PBIP_FILENAME = "modified_pbip.zip"

# UI Text
TITLE = "💡Your PowerBI Assistant"
API_KEY_LABEL = "OpenAI API Key"
REQUEST_LABEL = "Enter your request:"
FILE_UPLOAD_LABEL = "Upload the PBIP folder (as a .zip file)"
SUBMIT_BUTTON_LABEL = "Submit"

# Error Messages
API_KEY_ERROR = "Please enter your OpenAI API key!"
FILE_UPLOAD_ERROR = "Please upload the PBIP folder as a .zip file!"
UNSUPPORTED_REQUEST_ERROR = """ℹ️ Sorry, your request is beyond my capabilities. As a PowerBI Assistant, I specialize in:
- Writing documentation for specific platforms
- Adding a README page to existing PowerBI reports
- Performing modifications such as standardizing the visuals of a dashboard
Please adjust your request and try again."""

# Success Messages
MODIFICATION_SUCCESS = "PBIP folder modified successfully!" 
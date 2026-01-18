"""Configuration constants for the PowerBI Assistant application."""

# Documentation section titles

#DOC_DASHBOARD_OVERVIEW = "h1. Aperçu du tableau de bord"
#DOC_DETAILED_INFO = "h1. Informations détaillées"
#DOC_DATASET_INFO = "h1. Informations sur le jeu de données"
#DOC_TABLE_SOURCE = "h2. Source des tables"
#DOC_MEASURES_SUMMARY = "h2. Résumé des mesures"
#DOC_DETAILED_MEASURES = "h2. Détails des mesures par colonne"

# Default values
DEFAULT_LANGUAGE = "English"
DEFAULT_PLATFORM = "Confluence"
DEFAULT_MODEL = "gpt-5"
SUPPORTED_MODELS = ["gpt-5", "gpt-4.1", "gpt-3.5-turbo"]
SUPPORTED_TASKS = ["README", "Documentation"]
DEFAULT_REQUEST_TEXT = "I want to add a README page to the PowerBI report."
FILE_UPLOAD_LABEL = "Upload the PBIP folder (as a .zip file)"
FILE_UPLOAD_LABEL_PDF = "Upload the PowerBI report (as a .pdf file)"
FILE_PDF_UPLOAD_LABEL = "Upload the PDF file"

# File paths and names
DOCUMENTATION_FILENAME = "Documentation.txt"
MODIFIED_PBIP_FILENAME = "modified_pbip.zip"

# UI Text
TITLE = "💡Your PowerBI Assistant"
DETAILS_APP = """
This assistant analyzes Power BI reports and automatically generates two types of documentation :

📘 1. README Page embedded in the Power BI file
A clear summary within the Power BI file, including :
- Dashboard objectives
- Overview of the pages
- Detailed KPIs per page

📄 2. Complete Detailed Documentation
A comprehensive guide to understand and maintain the Power BI model :
- Global view of the dashboard and its pages
- Key information about the dataset: table sources, measure summaries, and DAX details per column.
"""
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
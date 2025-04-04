FUNCTION_DESCRIPTIONS = [
    {
        "name": "add_read_me",
        "description": "Add a read me page to summarize the dashboard",
        "parameters": {
            "type": "object",
            "properties": {
                "dashboard_summary": {
                    "type": "string",
                    "description": "A summary description of the entire dashboard."
                },
                "pages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "page_name": {
                                "type": "string",
                                "description": "The name of the dashboard page, populated from the displayName of the sections in the provided JSON."
                            },
                            "page_summary": {
                                "type": "string",
                                "description": "A summary description of the page."
                            },
                            "visuals": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "kpi_name": {
                                            "type": "string",
                                            "description": "The name of the KPI or visual on the page."
                                        },
                                        "kpi_definition": {
                                            "type": "string",
                                            "description": "The definition of the KPI or visual."
                                        }
                                    },
                                    "required": ["kpi_name", "kpi_definition"]
                                },
                                "description": "A list of visuals/KPIs on the page with their definitions."
                            }
                        },
                        "required": ["page_name", "page_summary", "visuals"]
                    }
                }
            },
            "required": ["dashboard_summary", "pages"]
        }
    },
    {
        "name": "summary_in_target_platform",
        "description": "Generate documentation for a Power BI report tailored to a specified platform and language.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "The language in which the documentation should be written (e.g., English, French)."
                },
                "platform": {
                    "type": "string",
                    "description": "The target platform where the documentation will be used (e.g., Confluence, SharePoint)."
                }
            }
        }
    },
    {
        "name": "slicer_uniformisation_in_report",
        "description": "Modify the JSON file of the report to uniformize the slicers format based on the user's instructions",
        "parameters": {}
    },
]
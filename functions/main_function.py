import openai
from streamlit_app import *

function_descriptions = [
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
        "name": "summary_in_confluence",
        "description": "Summarize key details and metrics in Confluence.",
        "parameters": {}
    },
    {
        "name": "slicer_uniformisation_in_report",
        "description": "Modify the JSON file of the report to uniformize the slicers format based on the user's instructions",
        "parameters": {
            "type": "object",
            "properties": {
                "report_json": {
                    "type": "string",
                    "description": "The content of the JSON file of the Power BI report"
                },
                "instructions": {
                    "type": "string",
                    "description" : "The user's intructions that specify how to modify the report"
                }
            },
            "required": ["report_json", "instructions"]
        }
    },
]

def generate_completion(user_input):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
        functions=function_descriptions,
        function_call="auto",  # Let the model decide if it needs to call the function
    )
    return completion.choices[0].message if completion.choices else {}

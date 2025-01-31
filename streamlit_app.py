import streamlit as st
import openai
import json
import zipfile
import io
import os

import json

def extract_relevant_elements_dashboard_summary(json_data):
    extracted_data = {
        "config": json_data.get("config", {}),
        "sections": []
    }

    for section in json_data.get("sections", []):
        # only include the pages which are not hidden in the dashabord
        page_config = json.loads(section['config'])
        if page_config.get('visibility')!=1:
            # Store displayName to know the section/page name
            section_summary = {
                "displayName": section.get("displayName", ""),
                "filters": section.get("filters", ""),
                "ordinal": section.get("ordinal", ""),
                "visualContainers": []
            }
            
            # Process each visual container in the section
            for visual in section.get("visualContainers", []):
                # Parse config if it's a string
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)

                    visual_type_to_be_excluded = ['actionButton', 'image', 'shape']
                    if config_data.get("singleVisual", {}).get("visualType", "") not in visual_type_to_be_excluded:
                        # Extract relevant visual properties
                        visual_summary = {
                            "visualType": config_data.get("singleVisual", {}).get("visualType", ""),
                            "projections": config_data.get("singleVisual", {}).get("projections", []),
                            "prototypeQuery": config_data.get("singleVisual", {}).get("prototypeQuery", {}),
                            "title": config_data.get("vcObjects", {}).get("title", []),
                            "filters": visual.get("filters", [])
                        }
                        
                        # Add visual summary if it has useful data
                        if any(visual_summary.values()):
                            section_summary["visualContainers"].append(visual_summary)

    extracted_data["sections"].append(section_summary)

    return extracted_data

def extract_relevant_parts_dataset(json_dataset):
    model = json_dataset.get('model', {})
    # Initialize the extracted dataset
    extracted_json_dataset = {       
        "tables": {
            "expressions": model.get("expressions", []),
            "table_partitions": []
        },
        "measures": []
    }

    # Define the keywords to exclude
    excluded_keywords = ["LocalDateTable", "DateTableTemplate"]

    # Filter tables to exclude ones containing the excluded keywords
    for table in model.get("tables", []):
        if not any(keyword in table.get('name', '') for keyword in excluded_keywords):
            # Add table partitions if they exist
            partitions = table.get('partitions', [])
            if partitions:
                extracted_json_dataset["tables"]["table_partitions"].extend(partitions)

            # Add measures if they exist
            if "measures" in table:
                print(f"The table '{table['name']}' contains measures.")
                extracted_json_dataset["measures"].extend(table["measures"])
    
    return extracted_json_dataset

def extract_measures_name_and_expression(elements):
    result = []
    for element in elements:
        name = element.get('name')
        # Combine the non-empty parts of the 'expression' list into a single string
        expression = " ".join(part.strip() for part in element.get('expression', []) if part.strip())
        result.append({'name': name, 'expression': expression})
    return result

def extract_dashboard_by_page(json_data):
    sections_list = []

    for section in json_data.get("sections", []):
        # only include the pages which are not hidden in the dashboard
        page_config = json.loads(section['config'])
        if page_config.get('visibility') != 1:
            # Store displayName to know the section/page name
            section_summary = {
                "displayName": section.get("displayName", ""),
                "filters": section.get("filters", ""),
                "ordinal": section.get("ordinal", ""),
                "visualContainers": []
            }

            # Process each visual container in the section
            for visual in section.get("visualContainers", []):
                # Parse config if it's a string
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)

                    visual_type_to_be_excluded = ['actionButton', 'image', 'shape', 'textbox', '']
                    if config_data.get("singleVisual", {}).get("visualType", "") not in visual_type_to_be_excluded:
                        # Extract relevant visual properties
                        visual_summary = {
                            "visualType": config_data.get("singleVisual", {}).get("visualType", ""),
                            "projections": config_data.get("singleVisual", {}).get("projections", []),
                            "prototypeQuery": config_data.get("singleVisual", {}).get("prototypeQuery", {}),
                            "title": config_data.get("vcObjects", {}).get("title", []),
                            "filters": visual.get("filters", [])
                        }

                        # Add visual summary if it has useful data
                        if any(visual_summary.values()):
                            section_summary["visualContainers"].append(visual_summary)

            # Add the section's displayName and extracted_data to the list
            sections_list.append({
                "displayName": section.get("displayName", ""),
                "extracted_data": section_summary
            })

    return sections_list

def extract_relevant_elements_slicer_unif(json_data):
    extracted_data = {
        #"config": json_data.get("config", {}),
        "sections": []
    }
    for section in json_data.get("sections", []):
        # Store displayName to know the section/page name
        section_summary = {
            "displayName": section.get("displayName", ""),
            "visualContainers": []
        }
        # Process each visual container in the section
        for visual in section.get("visualContainers", []):
            # Parse config if it's a string
            config_data = visual.get("config", {})
            if isinstance(config_data, str):
                config_data = json.loads(config_data)
            # Extract relevant visual properties
            visual_type = config_data.get("singleVisual", {}).get("visualType", "")
            if visual_type in ["slicer", "advancedSlicerVisual"]:
                visual_summary = {
                    "name": config_data.get("name", ""),
                    "visualType": visual_type,
                    "prototypeQuery": config_data.get("singleVisual", {}).get("prototypeQuery", {}),
                    "objects": config_data.get("singleVisual", {}).get("objects", {}),
                    "vcObjects": config_data.get("singleVisual", {}).get("vcObjects", {})
                }
                # Add visual summary if it has useful data
                section_summary["visualContainers"].append(visual_summary)
        # Add section summary if it has relevant visual containers
        if section_summary["visualContainers"]:
            extracted_data["sections"].append(section_summary)
    return extracted_data

import zipfile
import io
import os

# Function to write the modified JSON back to the original folder structure and re-zip the file
def write_modified_zip(modified_json, report_json_path, folder_path):
    # Write the modified JSON content back to report.json
    with open(report_json_path, 'w', encoding='utf-8') as file:
        file.write(modified_json)

    # Create a new zip file with the modified content
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        # Walk the folder and add everything back to the zip
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                new_zip.write(file_path, arcname=arcname)

    zip_buffer.seek(0)  # Move to the beginning of the file for download
    return zip_buffer

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

def generate_completion(user_input):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
        functions=function_descriptions,
        function_call="auto",  # Let the model decide if it needs to call the function
    )
    return completion.choices[0].message if completion.choices else {}

from streamlit_app import *
import streamlit as st
import openai
import json
import ast

def global_summary_dashboard(extracted_json_by_page, target_platform="Confluence", language="English"):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            f"Create a concise and professional summary of a Power BI report in approximately 150 words in {language} based on the provided Dashboard Information:\n\n"
            "**Dashboard Information:**\n"
            f"{extracted_json_by_page}\n\n"
            "### Instructions:\n"
            "- Write a clear and comprehensive summary that captures the **dashboard's purpose**.\n"
            "- Ensure the summary accurately reflects the content provided and **do not invent anything**.\n"
            f"- The summary must be appropriately styled for **{target_platform}**.\n"
            "- You should only return a single paragraph of the summary without adding anything else.\n\n"
            "### Example Output:\n"
            "\"This dashboard provides a comprehensive overview of key performance indicators, highlighting recent trends, achievements, and areas requiring attention. "
            "It serves as a powerful tool to monitor progress, identify growth opportunities, and support strategic decision-making across critical business domains.\"\n"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are an assistant that specializes in summarizing Power BI dashboards. Your task is to create a concise yet comprehensive summary of the dashboard based on the information provided for its different pages. Ensure the summary is accurate, well-structured, and tailored for the specified target platform."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"

def summarize_dashboard_by_page(extracted_json_by_page, target_platform="Confluence", language="English"):
    result_summary = ""
    page_overview_dict = {}  # Dictionary to store Page Overview content by page_name

    for page_data in extracted_json_by_page:
        page_name = page_data['displayName']
        extracted_json_of_the_page = page_data['extracted_data']

        try:
            # Define prompt for OpenAI
            prompt = (
                "I will provide you with a JSON file, and you need to retrieve the following information from the file:\n\n"
                "### Instructions\n"
                "1. **Page Overview**\n"
                "   - Write a overall purpose of the page.\n\n"
                "2. **Visualizations**\n"
                "   - List all the visuals on the page, what they represent, and how users can interpret them.\n\n"
                "3. **Filtering**\n"
                "   - Explain slicers, filters, or date pickers used on the page.\n\n"
                "4. **Scenarios for Interpretation**\n"
                "   - Provide examples to guide users on how to interpret the dashboard effectively.\n\n"
                f"### Provided JSON\n{extracted_json_of_the_page}\n\n"
                "### Important Notes\n"
                "- If certain information is not available in the JSON file, omit it without inventing data.\n"
                f"- Ensure the retrieved information is structured in {language} and formatted appropriately for {target_platform}.\n\n"
                "### Expected Output Format\n"
                "- Use headings and bullet points to organize the output.\n"
                "- Ensure clear and concise explanations for each section."
            )

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that extracts key information from Power BI pbip reports' JSON files."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract and append the summary to the result string
            summary = response['choices'][0]['message']['content']
            result_summary += f"### {page_name}\n{summary}\n\n"

            # Use a structured approach to extract "Page Overview"
            structured_prompt = (
                "Extract only the **Page Overview** and **Visualizations** from the following content and return it in plain text format:\n\n"
                "- For the content under the Visualizations section, ignore slicers and focus only on visuals such as charts and tables that provide meaningful insights into the dashboard.\n\n"
                f"{summary}\n\n"
            )

            # Extract only the Page Overview using another API call
            overview_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content extractor specializing in summarizing key sections."},
                    {"role": "user", "content": structured_prompt}
                ]
            )
            page_overview = overview_response['choices'][0]['message']['content'].strip()

            # Store the Page Overview in the dictionary
            page_overview_dict[page_name] = page_overview

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    # Return both result_summary and page_overview_dict
    return result_summary, page_overview_dict

def summarize_table_source(table_content, target_platform="Confluence", language="English"):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            f"Extract and list all table names and their corresponding sources from the provided TABLE Content in {language}.\n"
            "- The table names are located in the 'name' key of each object under the 'table_partitions' key.\n"
            "- For each table, extract its 'source' from the 'source' key of the same object.\n"
            "- If the 'source' key includes parameters (e.g., 'server_id', 'database_id', 'storage_id'), match each parameter name with the 'name' key in the 'expressions' section of the TABLE Content to identify the parameter's value.\n"
            "- For parameters with dynamic or concatenated values, describe clearly how these values are combined.\n"
            "- Ensure that all tables listed in the TABLE Content are included in the summary, with none omitted.\n"
            "- Do not add any irrelevant information such as introductions or summaries.\n"
            f"- Format the summary appropriately for {target_platform}, ensuring it is clear, concise, and well-organized.\n\n"
            "### TABLE Content\n"
            f"{table_content}\n\n"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that specializes in extracting powerBI related information from json file."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def create_measures_overview_table(measures_content, target_platform="Confluence"):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            "**Create a table** with the following columns:\n"
            "- 'Name of the Measure'\n"
            "- 'Measure Formula'\n"
            "- 'Description'\n\n"
            "### Instructions\n"
            "1. The formulas for each measure can be found under the 'expression' key in the MEASURES content.\n"
            "2. For the 'Measure Formula' column, extract the exact formula from the 'expression' key without modifying or omitting anything.\n"
            "3. Ensure all measures presented in the MEASURES content are included in the 'Name of the Measure' column.\n"
            "4. Based on your understanding of the measure, write a short explanation of the measure's purpose in the 'Description' column\n"
            "5. For the output, **only return the table** without any additional text.\n"
            f"6. Ensure the table is formatted appropriately for {target_platform}\n\n"
            "### Example\n"
            "If a measure is calculated as follows:\n"
            "`Whitelisted Clients = CALCULATE(COUNTROWS('dim_client'), dim_client[is_whitelisted] = \"yes\")`\n\n"
            "The output of the table should look like this:\n\n"
            "| Name of the Measure   | Measure Formula                                                | Description                               |\n"
            "|-----------------------|-------------------------------------------------------------|-------------------------------------------|\n"
            "| Whitelisted Clients   | CALCULATE(COUNTROWS('dim_client'), dim_client[is_whitelisted] = \"yes\") | The measure calculates the total number of whitelisted clients |\n\n"
            "### MEASURES\n"
            f"{measures_content}\n\n"
            "### Output\n"
            "Generate the table in the format shown above."
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are an assistant that specializes in summarizing the measures in Power BI dashboards."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def create_measures_by_column_table(measures_content, target_platform="Confluence"):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            "**Create a table** with three columns: 'Name of the Measure', 'Source Table', and 'Used Columns', based on the measures provided below.\n\n"
            "### Example\n"
            "If a measure is calculated as follows:\n"
            "`Whitelisted Clients = CALCULATE(COUNTROWS('dim_client'), dim_client[is_whitelisted] = \"yes\")`\n\n"
            "The output of the second table should look like this:\n\n"
            "| Name of the Measure   | Source Table | Used Columns       |\n"
            "|-----------------------|--------------|--------------------|\n"
            "| Whitelisted Clients   | dim_client   | pky_client         |\n"
            "| Whitelisted Clients   | dim_client   | is_whitelisted     |\n\n"
            "### Instructions\n"
            "- Each row in the table should correspond to one column from the 'Used Columns' of a measure. If a measure uses multiple columns, create separate rows for each column, repeating the measure's name and source table.\n"
            "- For the output, **only return the table** without any additional text.\n"
            f"- Ensure the table is formatted appropriately for {target_platform}.\n\n"
            "### MEASURES\n"
            f"{measures_content}\n\n"
            "### Output\n"
            "Generate the table in the format shown above."
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are an assistant that specializes in summarizing the measures in Power BI dashboards."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"

def unif_slicers(extracted_report, instructions) :

    prompt = """Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI et leur fichier JSON. 
    Je vais te fournir une liste de morceaux de fichiers jsons qui decrivent la configuration des filtres dans un dashboard power bi. 
    Ton role est de modifier les arguments dans les morceaux de fichiers jsons du rapport fourni selon les instructions fournies par l'utilisateur.
    L'objectif final est d'uniformiser les filtres du rapport en se basant sur le format du filtre precise par l'utilisateur.
    Tu ne dois absolument pas faire d'autres modifications que celles precisees par l'utilisateur.
    Si tu ne sais pas comment faire les bonnes modifications, reponds 'Modification impossible'""".replace('\n', '')

    response = openai.ChatCompletion.create(
    model="ft:gpt-3.5-turbo-0125:personal::AWNyxMxO",
    messages=[
        {"role": "system", "content": f"{prompt}"},
        {"role": "user", "content": f"{instructions} en modifiant les extraits du fichier JSON du rapport power BI fourni. Extraits du fichier JSON ={extracted_report}"}
    ]
    )
    json_reponse = response['choices'][0]['message']['content']
    json_reponse_clean = json.dumps(ast.literal_eval(json_reponse), ensure_ascii=False)

    return json_reponse_clean


def update_json_unif_slicers(json_to_update, modified_parts):

    keys_to_update = ['visualType', 'prototypeQuery', 'objects', 'vcObjects']

    # Parcourir les sections modifiées
    for section in modified_parts.get('sections', []):
        modified_visual_containers = section.get('visualContainers', [])

        # Rechercher la section correspondante dans l'original
        for original_section in json_to_update.get('sections', []):
            if section.get('displayName') == original_section.get('displayName'):
                original_visual_containers = original_section.get('visualContainers', [])

                # Parcourir les visualContainers modifiés
                for modified_container in modified_visual_containers:
                    #modified_name = modified_container.get('name')
                    modified_name = modified_container["prototypeQuery"]["Select"][0]["NativeReferenceName"]

                    # Mettre à jour le conteneur correspondant dans l'original
                    for original_container in original_visual_containers:
                        original_config = json.loads(original_container.get('config', '{}'))
                        #original_name = original_config.get('name')
                        original_name = original_config["singleVisual"]["prototypeQuery"]["Select"][0]["NativeReferenceName"]
                        if original_name == modified_name:
                            # Mettre à jour uniquement les parties spécifiées
                            for key in keys_to_update :
                                original_config['singleVisual'][key] = modified_container[key]
                            # Réécrire la configuration mise à jour
                            original_container['config'] = json.dumps(original_config, ensure_ascii=False)

    return json_to_update
    
import json
import openai

def prepare_arguments_add_read_me(kpis, function_descriptions):
    # Run the function call with the extracted KPI data
    add_read_me_output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"{kpis}"
            }
        ],
        functions=function_descriptions,
        function_call={"name": "add_read_me", "arguments": json.dumps({"kpis": kpis})}
    )
    return add_read_me_output.choices[0].message["function_call"]["arguments"]

def prepare_arguments_summary_in_target_platform(user_prompt, function_descriptions):
    # Run the function call with the extracted KPI data
    add_read_me_output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"{user_prompt}"
            }
        ],
        functions=function_descriptions,
        function_call={"name": "summary_in_target_platform", "arguments": json.dumps({"kpis": kpis})}
    )
    return add_read_me_output.choices[0].message["function_call"]["arguments"]

def add_read_me(dashboard_summary, pages):
    # Define the template directly in the code
    template = {
        "config": "{\"version\":\"5.37\",\"themeCollection\":{\"baseTheme\":{\"name\":\"CY22SU03\",\"version\":\"5.31\",\"type\":2}},\"activeSectionIndex\":0,\"defaultDrillFilterOtherVisuals\":true,\"filterSortOrder\":3,\"linguisticSchemaSyncVersion\":2,\"settings\":{\"useNewFilterPaneExperience\":true,\"allowChangeFilterTypes\":true,\"useStylableVisualContainerHeader\":true,\"exportDataMode\":1,\"allowDataPointLassoSelect\":false,\"filterPaneHiddenInEditMode\":false,\"pauseQueries\":false,\"useEnhancedTooltips\":true},\"objects\":{\"section\":[{\"properties\":{\"verticalAlignment\":{\"expr\":{\"Literal\":{\"Value\":\"'Top'\"}}}}}],\"outspacePane\":[{\"properties\":{\"expanded\":{\"expr\":{\"Literal\":{\"Value\":\"false\"}}},\"visible\":{\"expr\":{\"Literal\":{\"Value\":\"false\"}}}}}]}}",
        "filters": "[]",
        "layoutOptimization": 0,
        "publicCustomVisuals": [],
        "resourcePackages": [
            {
                "resourcePackage": {
                    "disabled": False,
                    "items": [
                        {
                            "name": "CY22SU03",
                            "path": "BaseThemes/CY22SU03.json",
                            "type": 202
                        }
                    ],
                    "name": "SharedResources",
                    "type": 2
                }
            }
        ],
        "sections": [
            {
                "config": "{}",
                "displayName": "Glossary",
                "displayOption": 1,
                "filters": "[]",
                "height": 720.00,
                "name": "88cbaa1e34d414c234a5",
                "visualContainers": [
                    {
                        "config": "{\"name\":\"677ff640e2128e7c8715\",\"layouts\":[{\"id\":0,\"position\":{\"x\":325.4878295609724,\"y\":0,\"z\":0,\"width\":654.4881177143293,\"height\":63.22425466292269}}],\"singleVisual\":{\"visualType\":\"textbox\",\"drillFilterOtherVisuals\":true,\"objects\":{\"general\":[{\"properties\":{\"paragraphs\":[{\"textRuns\":[{\"value\":\" DASHBOARD NAME\",\"textStyle\":{\"fontWeight\":\"bold\",\"fontSize\":\"20pt\"}}],\"horizontalTextAlignment\":\"center\"},{\"textRuns\":[{\"value\":\"\"}]}]}}]}}}",
                        "filters": "[]",
                        "height": 63.22,
                        "width": 654.49,
                        "x": 325.49,
                        "y": 0.00,
                        "z": 0.00
                    }
                ],
                "width": 1280.00
            }
        ]
    }

    # Initialize the y-position for the first textbox and spacing between textboxes
    y_position = 50
    horizontal_distince_between_textbox = 40

    # Dashboard Summary Textbox Configuration
    dashboard_summary_height = 80
    dashboard_summary_width = 1200
    dashboard_summary_config = {
        "config": json.dumps({
            "name": "dashboardSummaryBox",
            "layouts": [{"id": 0, "position": {"x": 10, "y": y_position, "z": 0, "width": dashboard_summary_width, "height": dashboard_summary_height}}],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": [{
                                "textRuns": [{
                                    "value": dashboard_summary,
                                    "textStyle": {"fontSize": "14pt"}
                                }]
                            }]
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": dashboard_summary_height,
        "width": dashboard_summary_width,
        "x": 10,
        "y": y_position,
        "z": 0
    }
    template["sections"][0]["visualContainers"].append(dashboard_summary_config)

    # Update y_position for the next textbox
    y_position += dashboard_summary_height + horizontal_distince_between_textbox

    # Create text for page overviews with reduced spacing
    page_summary_height = 50
    paragraphs = [{"textRuns": [{"value": "Page Overview", "textStyle": {"fontWeight": "bold", "fontSize": "14pt"}}]}]

    for page in pages:
        paragraphs.append({
            "textRuns": [
                {
                    "value": f"{page['page_name']}: ",  # Page name part
                    "textStyle": {
                        "fontSize": "12pt",
                        "fontWeight": "bold"  # Make it bold
                    }
                },
                {
                    "value": page['page_summary'],  # Page summary part
                    "textStyle": {
                        "fontSize": "12pt"  # Keep regular font for the summary
                    }
                }
            ]
        })
        page_summary_height += 20

    # Textbox for all page summaries
    page_summaries_config = {
        "config": json.dumps({
            "name": "pageSummariesBox",
            "layouts": [{"id": 0, "position": {"x": 10, "y": y_position, "z": 0, "width": 1200, "height": page_summary_height}}],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": paragraphs
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": page_summary_height,
        "width": 1200,
        "x": 10,
        "y": y_position,
        "z": 0
    }
    template["sections"][0]["visualContainers"].append(page_summaries_config)

    # Update y_position for the next textbox
    y_position += page_summary_height + horizontal_distince_between_textbox

    # KPIs related text boxes
    x_position = 10
    max_width = 0

    for i, page in enumerate(pages):
        if i != 0 and i % 2 == 0:
            x_position = 10
            y_position += max_width + 30
            max_width = 0

        paragraphs = [{"textRuns": [{"value": page['page_name'], "textStyle": {"fontWeight": "bold", "fontSize": "14pt"}}]}]
        for visual in page['visuals']:
            paragraphs.append({
                "textRuns": [
                    {
                        "value": f"{visual['kpi_name']}: ",  # KPI name part
                        "textStyle": {
                            "fontSize": "12pt",
                            "fontWeight": "bold"  # Make the KPI name bold
                        }
                    },
                    {
                        "value": visual['kpi_definition'],  # KPI definition part
                        "textStyle": {
                            "fontSize": "12pt"  # Regular font for the KPI definition
                        }
                    }
                ]
            })

        textbox_height = 50 + len(page['visuals']) * 30
        max_width = max(max_width, textbox_height)

        kpi_textbox_config = {
            "config": json.dumps({
                "name": f"{page['page_name'].replace(' ', '')}KPIs",
                "layouts": [{"id": 0, "position": {"x": x_position, "y": y_position, "z": 0, "width": 600, "height": textbox_height}}],
                "singleVisual": {
                    "visualType": "textbox",
                    "drillFilterOtherVisuals": True,
                    "objects": {
                        "general": [{
                            "properties": {
                                "paragraphs": paragraphs
                            }
                        }]
                    }
                }
            }),
            "filters": "[]",
            "height": textbox_height,
            "width": 600,
            "x": x_position,
            "y": y_position,
            "z": 0
        }
        template["sections"][0]["visualContainers"].append(kpi_textbox_config)
        x_position += 650

    page_height = y_position + textbox_height + 50 
    # Update the page height to reflect the total height
    template["sections"][0]["height"] = page_height

    return template

import zipfile
import os
import shutil
import json

# Function to handle the PBIP folder and extract report.json and model.bim
def extract_report_and_model(zip_file):
    # Extract the zip file
    extract_path = '/mnt/data/pbip_extracted/'

    # Each time, we first remove the entire directory and its contents
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    inner_folder_name = os.listdir(extract_path)[0]
    inner_folder_path = os.path.join(extract_path, inner_folder_name)
    # Print the contents of the inner folder
    inner_folder_contents = os.listdir(inner_folder_path)
    report_folder_path = None
    model_bim_path = None

    # Look for the folder that ends with '.Report' or '.SemanticModel'
    for folder in inner_folder_contents:
        full_folder_path = os.path.join(inner_folder_path, folder)
        if folder.endswith('.Report') and os.path.isdir(full_folder_path):
            report_folder_path = full_folder_path
        elif folder.endswith('.SemanticModel') and os.path.isdir(full_folder_path):
            model_folder_path = full_folder_path

    # Extract report.json
    if report_folder_path:
        report_json_path = os.path.join(report_folder_path, 'report.json')
        with open(report_json_path, 'r', encoding='utf-8') as file:
            report_json_content = json.load(file)
    else:
        report_json_content = None

    # Extract model.bim
    if model_folder_path:
        model_bim_path = os.path.join(model_folder_path, 'model.bim')
        if os.path.exists(model_bim_path):
            with open(model_bim_path, 'r', encoding='utf-8') as file:
                model_bim_content = json.load(file)
        else:
            model_bim_content = None

    return report_json_content, model_bim_content, inner_folder_path, report_json_path, model_bim_path

st.title('💡Your PowerBI Assistant')
# Sidebar for API key input
openai_api_key = st.sidebar.text_input('OpenAI API Key', type="password")
openai.api_key = openai_api_key

# Initialize a variable to store the modified JSON content
modified_json = None
# Form for user input and file upload
with st.form('pbip_form'):
    text = st.text_area('Enter your request:', 'I want to add a filter to each page of the PowerBI report.')
    zip_file = st.file_uploader('Upload the PBIP folder (as a .zip file)', type=['zip'])
    submitted = st.form_submit_button('Submit')
# Process the form submission
if submitted:
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    elif zip_file is None:
        st.warning('Please upload the PBIP folder as a .zip file!', icon='⚠')
    else:
        # Extract report.json and model.bim from the uploaded PBIP folder
        report_json_content, model_bim_content, inner_folder_path, report_json_path, model_bim_path = extract_report_and_model(zip_file)
        output = generate_completion(text)
        print(output.get("function_call", {}).get("name"))
        if output.get("function_call", {}).get("name") == "add_read_me":
            extracted_report = extract_dashboard_by_page(report_json_content)
            summary_dashboard, overview_all_pages = summarize_dashboard_by_page(extracted_report) 
            # st.write(overview_all_pages)          
            # Extract the arguments string and parse it into a dictionary
            arguments = prepare_arguments_add_read_me(overview_all_pages, function_descriptions)
            arguments_dict = json.loads(arguments)
            updated_report = add_read_me(arguments_dict['dashboard_summary'], arguments_dict['pages'])
            report_json_content['sections'].insert(0, updated_report["sections"][0])
            modified_json = json.dumps(report_json_content, indent=4)
        elif output.get("function_call", {}).get("name") == "summary_in_target_platform":
            language = json.loads(output.function_call.arguments).get("language")
            target_platform = json.loads(output.function_call.arguments).get("platform")
            print(f"the documentaion will be written in {language} in {target_platform}.")
            extracted_report = extract_dashboard_by_page(report_json_content)
            extracted_dataset = extract_relevant_parts_dataset(model_bim_content)
            extracted_measures = extract_measures_name_and_expression(extracted_dataset['measures'])
            summary_dashboard, overview_all_pages = summarize_dashboard_by_page(extracted_report, target_platform=target_platform, language=language)
            overall_summary = global_summary_dashboard(overview_all_pages, target_platform=target_platform, language=language)
            summary_table = summarize_table_source(extracted_dataset['tables'], target_platform=target_platform, language=language)
            summary_measure_overview = create_measures_overview_table(extracted_measures, target_platform)
            summary_measure_detailed = create_measures_by_column_table(extracted_measures, target_platform)          
            text_list = [
                "h1. Dashboard Overview",
                f"{overall_summary}\n\n",
                "h1. Detailed Information By Page",
                f"{summary_dashboard}\n\n",
                "h1. Dataset Key Information",
                "h2. Table Source",
                f"{summary_table}\n\n"
                "h2. Measures Summary",
                f"{summary_measure_overview}\n\n"
                "h2. Detailed Measure Information By Column",
                f"{summary_measure_detailed}\n\n"
            ]
            # Combine all summaries into a single file content
            file_content = "\n\n".join(text_list)
            # Convert the content to bytes
            file_bytes = file_content.encode('utf-8')
            # Create a downloadable link for the text file
            st.download_button(
                label="Download Generated Documentation",
                data=file_bytes,
                file_name="Documentation.txt",
                mime="text/plain"
            )
            # st.write(summary_dashboard)
        elif output.get("function_call", {}).get("name") == "slicer_uniformisation_in_report":
            # Call the function to modify the JSON file based on user input
            extracted_report = extract_relevant_elements_slicer_unif(report_json_content)
            model_response = unif_slicers(extracted_report, text)
            modified_parts = json.loads(model_response)
            updated_json = update_json_unif_slicers(report_json_content, modified_parts)
            modified_json = json.dumps(updated_json, ensure_ascii=False, indent=4) # Convert the Python dictionary back to a JSON string
        else:
            # Handle the case where the function call is unexpected or not implemented
            st.info("ℹ️ Sorry, your request is beyond my capabilities. As a PowerBI Assistant, I specialize in writing documentation for specific platforms, adding a README page to existing PowerBI reports, and performing modifications such as standardizing the visuals of a dashboard. Please adjust your request and try again.")
        if modified_json:
            # Write back the modified report.json and create the zip file
            modified_zip = write_modified_zip(modified_json, report_json_path, inner_folder_path)
            st.success('PBIP folder modified successfully!')
            
            # Provide a download button for the modified zip file
            st.download_button(
                label='Download Modified PBIP Folder',
                data=modified_zip,
                file_name='modified_pbip.zip',
                mime='application/zip'
            )

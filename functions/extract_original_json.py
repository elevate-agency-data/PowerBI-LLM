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
    model = json_dataset['model']
    # Initialize the extracted dataset
    extracted_json_dataset = {
        "expressions": model.get("expressions", []),
        "tables": []
    }
    
    # Define the keywords to exclude
    excluded_keywords = ["LocalDateTable", "DateTableTemplate"]
    
    # Filter tables to exclude ones containing the excluded keywords
    for table in model.get("tables", []):
        if not any(keyword in table['name'] for keyword in excluded_keywords):
            # Remove the 'annotations' attribute from columns if it exists
            if 'columns' in table:
                for column in table['columns']:
                    if 'annotations' in column:
                        del column['annotations']
            
            extracted_json_dataset["tables"].append(table)
    
    return extracted_json_dataset

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


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
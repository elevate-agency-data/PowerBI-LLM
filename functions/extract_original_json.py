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

def extract_relevant_parts_dataset(data):
    # Initialize a dictionary to hold extracted information
    relevant_parts = {
        "DataSources": [],
        "DAXCalculations": [],
        "Relationships": []
    }

    # Extract data sources
    if "expressions" in data.get("model", {}):
        for expression in data["model"]["expressions"]:
            relevant_parts["DataSources"].append({
                "Name": expression.get("name"),
                "Expression": expression.get("expression"),
                "QueryGroup": expression.get("queryGroup")
            })

    # Extract DAX calculations (calculated columns and measures)
    if "tables" in data.get("model", {}):
        for table in data["model"]["tables"]:
            # for column in table.get("columns", []):
            #     if column.get("type") == "calculated":
            #         relevant_parts["DAXCalculations"].append({
            #             "Table": table.get("name"),
            #             "Column": column.get("name"),
            #             "Expression": column.get("expression")
            #         })
            for measure in table.get("measures", []):
                relevant_parts["DAXCalculations"].append({
                    "Table": table.get("name"),
                    "Measure": measure.get("name"),
                    "Expression": measure.get("expression")
                })

    # Extract relationships between tables
    if "relationships" in data.get("model", {}):
        for relationship in data["model"]["relationships"]:
            relevant_parts["Relationships"].append({
                "FromTable": relationship.get("fromTable"),
                "FromColumn": relationship.get("fromColumn"),
                "ToTable": relationship.get("toTable"),
                "ToColumn": relationship.get("toColumn"),
                "JoinBehavior": relationship.get("joinOnDateBehavior", "standard")
            })

    return relevant_parts

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


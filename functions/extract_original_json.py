import json

def extract_relevant_elements_dashboard_summary(json_data):
    extracted_data = {
        "config": json_data.get("config", {}),
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
            visual_summary = {
                "visualType": config_data.get("singleVisual", {}).get("visualType", ""),
                "projections": config_data.get("singleVisual", {}).get("projections", []),
                "prototypeQuery": config_data.get("singleVisual", {}).get("prototypeQuery", {}),
                "columnProperties": config_data.get("singleVisual", {}).get("columnProperties", {}),
                "title": config_data.get("vcObjects", {}).get("title", []),
                "filters": visual.get("filters", [])
            }
            
            # Add visual summary if it has useful data
            if any(visual_summary.values()):
                section_summary["visualContainers"].append(visual_summary)

        # Add section summary if it has relevant visual containers
        if section_summary["visualContainers"]:
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

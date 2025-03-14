import json
import copy

def update_json_unif_slicers(json_to_update, modified_parts):
    """Update JSON with modified slicer parts"""
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
                    modified_name = modified_container["prototypeQuery"]["Select"][0]["NativeReferenceName"]

                    # Mettre à jour le conteneur correspondant dans l'original
                    for original_container in original_visual_containers:
                        original_config = json.loads(original_container.get('config', '{}'))
                        original_name = original_config["singleVisual"]["prototypeQuery"]["Select"][0]["NativeReferenceName"]
                        if original_name == modified_name:
                            # Mettre à jour uniquement les parties spécifiées
                            for key in keys_to_update:
                                original_config['singleVisual'][key] = modified_container[key]
                            # Réécrire la configuration mise à jour
                            original_container['config'] = json.dumps(original_config, ensure_ascii=False)

    return json_to_update 

def add_read_me(dashboard_summary, pages):
    """Add a README page to the PowerBI report"""
    # Define the template with the same base structure as the target
    template = {
        "config": "{\"version\":\"5.55\",\"themeCollection\":{\"baseTheme\":{\"name\":\"CY24SU06\",\"version\":\"5.55\",\"type\":2}},\"activeSectionIndex\":0,\"defaultDrillFilterOtherVisuals\":true,\"linguisticSchemaSyncVersion\":2,\"settings\":{\"useNewFilterPaneExperience\":true,\"allowChangeFilterTypes\":true,\"useStylableVisualContainerHeader\":true,\"exportDataMode\":1,\"useEnhancedTooltips\":true},\"objects\":{\"section\":[{\"properties\":{\"verticalAlignment\":{\"expr\":{\"Literal\":{\"Value\":\"'Top'\"}}}}}],\"outspacePane\":[{\"properties\":{\"expanded\":{\"expr\":{\"Literal\":{\"Value\":\"false\"}}}}}]}}",
        "layoutOptimization": 0,
        "resourcePackages": [
            {
                "resourcePackage": {
                    "disabled": False,
                    "items": [
                        {
                            "name": "CY24SU06",
                            "path": "BaseThemes/CY24SU06.json",
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
                "height": 1600.00,
                "name": "88cbaa1e34d414c234a5",
                "visualContainers": [],
                "width": 1280.00
            }
        ]
    }

    # Set the distance variables
    title_height = 64
    dashboard_objective_height = 140
    page_overview_height = len(pages) * 55
    kpi_section_header = 46
    y_position = 0
    gap_between_sections = 20

    # 1. Add the title section with dark background
    title_config = {
        "config": json.dumps({
            "name": "677ff640e2128e7c8715",
            "layouts": [{
                "id": 0,
                "position": {"x": 0, "y": y_position, "z": 0, "width": 1280, "height": title_height}
            }],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": [{
                                "textRuns": [{
                                    "value": " DASHBOARD SUMMARY",
                                    "textStyle": {
                                        "fontWeight": "bold",
                                        "fontSize": "20pt",
                                        "color": "#ffffff"
                                    }
                                }],
                                "horizontalTextAlignment": "center"
                            }]
                        }
                    }]
                },
                "vcObjects": {
                    "background": [{
                        "properties": {
                            "color": {
                                "solid": {
                                    "color": {"expr": {"Literal": {"Value": "'#252423'"}}}
                                }
                            }
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": title_height,
        "width": 1280.00,
        "x": 0.00,
        "y": 0.00,
        "z": 0.00
    }
    template["sections"][0]["visualContainers"].append(title_config)

    # 2. Add the dashboard objective section
    y_position += title_height
    objective_config = {
        "config": json.dumps({
            "name": "dashboardSummaryBox",
            "layouts": [{
                "id": 0,
                "position": {"x": 0, "y": y_position, "z": 1000, "width": 1280, "height": dashboard_objective_height}
            }],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": [
                                {"textRuns": [{"value": ""}]},
                                {"textRuns": [{
                                    "value": "Dashboard Objective",
                                    "textStyle": {"fontWeight": "bold", "fontSize": "20pt"}
                                }]},
                                {"textRuns": [{
                                    "value": dashboard_summary,
                                    "textStyle": {"fontSize": "14pt"}
                                }]}
                            ]
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": dashboard_objective_height,
        "width": 1280.00,
        "x": 0.00,
        "y": y_position,
        "z": 1000.00
    }
    template["sections"][0]["visualContainers"].append(objective_config)

    # 3. Add the page overview section
    y_position += dashboard_objective_height + gap_between_sections
    page_overview_config = {
        "config": json.dumps({
            "name": "pageSummariesBox",
            "layouts": [{
                "id": 0,
                "position": {"x": 0, "y": y_position, "z": 2000, "width": 1280, "height": page_overview_height}
            }],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": [
                                {"textRuns": [{
                                    "value": "Page Overview",
                                    "textStyle": {"fontWeight": "bold", "fontSize": "20pt"}
                                }]},
                                *[{"textRuns": [
                                    {
                                        "value": f"{page['page_name']}: ",
                                        "textStyle": {"fontSize": "14pt", "fontWeight": "bold"}
                                    },
                                    {
                                        "value": page['page_summary'],
                                        "textStyle": {"fontSize": "14pt"}
                                    }
                                ]} for page in pages]
                            ]
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": page_overview_height,
        "width": 1200.00,
        "x": 0.00,
        "y": y_position,
        "z": 2000.00
    }
    template["sections"][0]["visualContainers"].append(page_overview_config)

    # 4. Add KPI header and sections
    y_position += page_overview_height + gap_between_sections
    
    # Add KPI header text
    kpi_header_config = {
        "config": json.dumps({
            "name": "kpiHeader",
            "layouts": [{
                "id": 0,
                "position": {
                    "x": 0,
                    "y": y_position,
                    "z": 2500,
                    "width": 1280,
                    "height": kpi_section_header
                }
            }],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": [
                                {"textRuns": [{
                                    "value": "Detailed KPIs by Page",
                                    "textStyle": {"fontWeight": "bold", "fontSize": "20pt"}
                                }]}
                            ]
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": kpi_section_header,
        "width": 1280.00,
        "x": 0.00,
        "y": y_position,
        "z": 2500
    }
    template["sections"][0]["visualContainers"].append(kpi_header_config)
    
    y_position += kpi_section_header

    # Add individual KPI sections for each page
    for i, page in enumerate(pages):
        x_position = 0
        kpi_height = len(page['visuals']) * 30 if len(page['visuals']) > 5 else len(page['visuals']) * 38
        kpi_config = {
            "config": json.dumps({
                "name": f"{page['page_name'].replace(' ', '')}KPIs",
                "layouts": [{
                    "id": 0,
                    "position": {
                        "x": x_position,
                        "y": y_position,
                        "z": 3000 + i * 1000,
                        "width": 1280, 
                        "height": kpi_height
                    }
                }],
                "singleVisual": {
                    "visualType": "textbox",
                    "drillFilterOtherVisuals": True,
                    "objects": {
                        "general": [{
                            "properties": {
                                "paragraphs": [
                                    {"textRuns": [{
                                        "value": page['page_name'],
                                        "textStyle": {"fontWeight": "bold", "fontSize": "14pt"}
                                    }]},
                                    *[{"textRuns": [
                                        {
                                            "value": "• ",
                                            "textStyle": {"fontSize": "14pt"}
                                        },
                                        {
                                            "value": f"{visual['kpi_name']}: ",
                                            "textStyle": {"fontSize": "14pt", "fontWeight": "bold"}
                                        },
                                        {
                                            "value": visual['kpi_definition'],
                                            "textStyle": {"fontSize": "14pt"}
                                        }
                                    ]} for visual in page['visuals']]
                                ]
                            }
                        }]
                    }
                }
            }),
            "filters": "[]",
            "height": kpi_height,
            "width": 1280.00, 
            "x": x_position,
            "y": y_position,
            "z": 3000 + i * 1000
        }
        template["sections"][0]["visualContainers"].append(kpi_config)
        
        # Update the page height to reflect the total height
        y_position += kpi_height + gap_between_sections
        template["sections"][0]["height"] = y_position

    return template

##### Unif slicers #####

def extract_json_elements_source_visual(json_data, source_page_name, source_visual_id, df):
    for section in json_data.get("sections", []):
        page_name = section.get("displayName", "")
        if page_name == source_page_name :
            for visual in section.get("visualContainers", []) :
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)
                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']
                if visual_type in visual_type_to_be_included :
                    visual_id = config_data.get("name", {})
                    if visual_id == source_visual_id :
                        visual_summary = {
                            "visualType": visual_type,
                            "objects": config_data.get("singleVisual", {}).get("objects", {}),
                            "vcObjects": config_data.get("singleVisual", {}).get("vcObjects", {})
                        }
                
    return visual_summary


def update_target_visuals(original_json_data, source_visual_elements, source_page_name, source_visual_id, target_page_name, target_visual_id, df):
    for section in original_json_data.get("sections", []):
        page_name = section.get("displayName", "")
        if page_name == target_page_name:
            for visual in section.get("visualContainers", []):
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)

                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']

                if visual_type in visual_type_to_be_included:
                    visual_id = config_data.get("name", {})
                    if visual_id == target_visual_id:
                        # Crée une copie indépendante des éléments source
                        local_visual_elements = copy.deepcopy(source_visual_elements)
                        config_data["singleVisual"].update(local_visual_elements)

                        source_title_present = df[(df["visual id"] == source_visual_id) & (df["page name"] == source_page_name)]["title present"].values[0]
                        source_header_present = df[(df["visual id"] == source_visual_id) & (df["page name"] == source_page_name)]["header present"].values[0]

                        target_header_present = df[(df["visual id"] == target_visual_id) & (df["page name"] == target_page_name)]["header present"].values[0]

                        target_visual_name = df[df["visual id"] == target_visual_id]["visual name"].values[0]

                        # Modifie le titre si nécessaire
                        if source_title_present == True:
                            #config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"] = {"expr": {"Literal": {"Value": f"{visual_name}"}}}
                            updated_config_data = copy.deepcopy(config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"])
                            updated_config_data = {"expr": {"Literal": {"Value": f"{target_visual_name}"}}}
                            config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"] = updated_config_data
                            print(config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"])


                        # Modifie le header si présent dans la source
                        if source_header_present == True:
                            # Crée une copie indépendante du header
                            #config_data["singleVisual"]["objects"]["header"][0]["properties"]["text"] = {"expr": {"Literal": {"Value": f"{visual_name}"}}}
                            updated_config_data = copy.deepcopy(config_data["singleVisual"]["objects"]["header"][0]["properties"]["text"])
                            updated_config_data = {"expr": {"Literal": {"Value": f"{target_visual_name}"}}}
                            config_data["singleVisual"]["objects"]["header"][0]["properties"]["text"] = updated_config_data


                        # Si le header est dans le target mais pas dans la source
                        if target_header_present == True and 'text' not in source_visual_elements["objects"]["header"][0]["properties"]:
                            # Crée une copie indépendante du header
                            target_header = copy.deepcopy(config_data["singleVisual"]["objects"]["header"][0]["properties"])
                            target_header.update({"text": {"expr": {"Literal": {"Value": f"{target_visual_name}"}}}})
                            config_data["singleVisual"]["objects"]["header"][0]["properties"] = target_header
                        
    
                        visual["config"] = json.dumps(config_data, ensure_ascii=False)
                        
    return original_json_data


def modify_json(original_json_data, dict_slicers, df) :
    source_page_name = dict_slicers["source"]["source_page"]
    source_visual_id = dict_slicers["source"]["source_visual"]
    source_visual_elements = extract_json_elements_source_visual(original_json_data, source_page_name, source_visual_id, df)
    for target_visual in dict_slicers["target"] :
        target_page_name = target_visual["target_page"]
        target_visual_id = target_visual["target_visual"]
        updated_json = update_target_visuals(original_json_data, source_visual_elements, source_page_name, source_visual_id, target_page_name, target_visual_id, df)
    print("json updated for all visuals")
    return updated_json

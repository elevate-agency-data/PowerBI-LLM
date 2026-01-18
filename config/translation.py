PROMPT_STRINGS = {
    "English": {
        "name_measure": "Name of the measure",
        "measure_formula" : "Measure formula",
        "measure_description": "Description",
        "source_table": "Source Table",
        "used_columns": "Used Columns",
        "overview": "Page Overview",
        "detail_info": "h1. Detailed Information",
        "dataset_info": "h1. Dataset Information",
        "table_source": "h2. Table Source",
        "measure_suma": "h2. Measures Summary",
        "detail_measure": "h2. Detailed Measures by Column",
        "app_title": "💡Your PowerBI Assistant",
        "app_description": """This assistant analyzes Power BI reports and automatically generates two types of documentation :
                            📘 1. README Page embedded in the Power BI file
                            A clear summary within the Power BI file, including :
                            - Dashboard objectives
                            - Overview of the pages
                            - Detailed KPIs per page

                            📄 2. Complete Detailed Documentation
                            A comprehensive guide to understand and maintain the Power BI model :
                            - Global view of the dashboard and its pages
                            - Key information about the dataset: table sources, measure summaries, and DAX details per column.""",
        "readme" : "Generate README",
        "documentation" : "Generate Description",
        "detail_kpi": "Detailed KPIs by Page",
        "page_overview": "Page Overview",
        "dash_objtiv": "Dashboard Objective"
                            
    },
    "French": {
        "name_measure": "Nom de la mesure",
        "measure_formula" : "Formule de la mesure",
        "measure_description": "Description",
        "source_table": "Table source",
        "used_columns": "Colonnes utilisées",
        "overview": "h1. Aperçu du tableau de bord",
        "detail_info": "h1. Informations détaillées",
        "dataset_info": "h1. Informations sur le jeu de données",
        "table_source": "h2. Source des tables",
        "measure_suma": "h2. Résumé des mesures",
        "detail_measure": "h2. Détails des mesures par colonne",
        "app_title": "💡Votre Assistant PowerBI",
        "app_description": """Cet assistant analyse les rapports Power BI et génère automatiquement deux types de documentation :
                            📘 1. Page README intégrée dans le fichier Power BI
                            Un résumé clair au sein du fichier Power BI, incluant :
                            - Objectifs du tableau de bord
                            - Aperçu des pages
                            - KPI détaillés par page

                            📄 2. Documentation détaillée complète
                            Un guide complet pour comprendre et maintenir le modèle Power BI :
                            - Vue globale du tableau de bord et de ses pages
                            - Informations clés sur le jeu de données : sources des tables, résumés des mesures et détails DAX par colonne.""",
        "readme" : "Générer le README",
        "documentation" : "Générer la description",
        "detail_kpi": "KPI détaillés par page",
        "page_overview": "Aperçu de la page",
        "dash_objtiv": "Objectif du tableau de bord"
    },
    "Chinese": {
        "name_measure": "措施名称",
        "measure_formula" : "测量公式",
        "measure_description": "描述",
        "source_table": "源表",
        "used_columns": "二手色谱柱",
        "overview": "h1. 仪表板概述",
        "detail_info": "h1. 详细信息",
        "dataset_info": "h1. 数据集信息",
        "table_source": "h2. 表来源",
        "measure_suma": "h2. 措施摘要",
        "detail_measure": "h2. 按列详细说明措施",
        "app_title": "💡您的 PowerBI 助手",
        "app_description" : """此助手可分析 Power BI 报表，并自动生成两种类型的文档：
                            📘 1. 嵌入 Power BI 文件的 README 页面
                            Power BI 文件中的清晰摘要，包括：
                            - 仪表板目标
                            - 各页面概述
                            - 每页的详细 KPI

                            📄 2. 完整的详细文档
                            了解和维护 Power BI 模型的综合指南：
                            - 仪表板及其页面的全局视图
                            - 有关数据集的关键信息：表来源、措施摘要和每列的 DAX 详细信息。""",
        "readme" : "生成自述文件",
        "documentation" : "生成说明",
        "detail_kpi": "每页详细的 KPI",
        "page_overview": "页面概述",
        "dash_objtiv": "仪表板目标"
    }
}

def t(language, key):
    fallback = "French"
    bundle = PROMPT_STRINGS.get(language, PROMPT_STRINGS[fallback])
    return bundle.get(key, PROMPT_STRINGS[fallback].get(key, key))
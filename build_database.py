import json
import pandas as pd

prompt = """Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI et leur fichier JSON. 
Je vais te fournir une liste de morceaux de fichiers jsons qui decrivent la configuration de chaque visuel dans un dashboard power bi. 
Ton role est de modifier les arguments dans les morceaux de fichiers jsons du rapport fourni selon les instructions fournies par l'utilisateur.
Tu ne dois pas faire d'autres modifications que celles precisees par l'utilisateur.
Tu dois absolument respecter le schema du JSON fourni.
Si tu ne sais pas comment modifier le fichier JSON, reponds 'Modification impossible'""".replace('\n', '')


##### Extraire les lignes config pour chaque visuel #####

visual_types = ["slicer",  "advancedSlicerVisual"]
json_path = "jsons_train/airbnb_same_as_cancellation.json"

def extraire_configs(json_path, visual_types):
    with open(json_path, 'r') as json_data :
        data = json.load(json_data)
    configs = []
    for section in data.get("sections", []):
        for visual_container in section.get("visualContainers", []):
            # Extraire le champ config
            config_str = visual_container.get("config", None)
            if config_str:
                # Charger le contenu de la configuration JSON
                config_data = json.loads(config_str)
                # Extraire le champ qui détermine le type de visuel
                single_visual = config_data.get("singleVisual", {})
                visual_type = single_visual.get("visualType", "")
                # Si la liste est vide ou si le type de visuel est dans la liste donnée, on ajoute le fichier config
                if not visual_types or visual_type in visual_types:
                    configs.append(config_data)
    return configs

test = extraire_configs("jsons_train/airbnb_same_as_cancellation.json", bdd_excel['filtre_visuels'][0])

####### Construire le template pour chaque exemple de la base ########

def template_json(instructions, json_path_before_change, json_path_after_change, visual_types, prompt):
# Fonction pour mettre en forme le prompt avec le json PBI
    # with open(json_path_before_change, 'r') as json_data :
    #     json_before_change = json.load(json_data)
    # try :
    #     with open(json_path_after_change, 'r') as json_data :
    #         json_after_change = json.load(json_data)
    # except :
    #     json_after_change = json_path_after_change

    json_before_change = extraire_configs(json_path_before_change, visual_types)
    json_after_change = extraire_configs(json_path_after_change, visual_types)

    template = {"messages": [
        {"role": "system", "content": f"{prompt}"}, 
        {"role": "user", "content": f"{instructions} en te basant sur le fichier JSON du rapport power BI fourni. Fichier JSON = {json_before_change}."}, 
        {"role": "assistant", "content": f"{json_after_change}"}]}

    final_json = json.dumps(template, indent=4)

    return final_json

# Test sur un rapport

instructions = "Ajoute un histogramme du nombre de user_id par pays"
json_path_before_change = "jsons_train/IT__web_bis.json"
json_path_after_change = "jsons_train/IT__web_bis_same_as_browser.json"
visual_types = ["slicer"]
processed_json = template_json(instructions, json_path_before_change, json_path_after_change, visual_types, prompt)
print(processed_json)

####### Construction de la base de données #######

bdd_excel = pd.read_excel("bdd/bdd_train_unif_filtres.xlsx")
bdd_excel['filtre_visuels'] = bdd_excel['filtre_visuels'].apply(lambda x: str(x).split(', '))
jsonl_path = 'bdd/bdd_jsons_train_unif_filtres.jsonl'

def build_bdd(bdd_excel, prompt, jsonl_path):
    bdd_excel['json_resultat'] = bdd_excel.apply(lambda row: template_json(row['instructions'], row['json_path_before_change'], row['json_path_after_change'], row['filtre_visuels'], prompt), axis=1)

    # On ajoute tous les jsons à un fichier jsonl
    with open(jsonl_path, 'w') as file:
        for item in bdd_excel['json_resultat']:
            json_obj = json.loads(item)
            json.dump(json_obj, file)
            file.write('\n')
    
build_bdd(bdd_excel, prompt, jsonl_path)

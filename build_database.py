import json
import pandas as pd


def template_json(instructions, json_path_before_change, json_path_after_change, prompt):
# Fonction pour mettre en forme le prompt avec le json PBI
    with open(json_path_before_change, 'r') as json_data :
        json_before_change = json.load(json_data)
    try :
        with open(json_path_after_change, 'r') as json_data :
            json_after_change = json.load(json_data)
    except :
        json_after_change = json_path_after_change

    template = {"messages": [
        {"role": "system", "content": f"{prompt}"}, 
        {"role": "user", "content": f"{instructions} en te basant sur le fichier JSON du rapport power BI fourni. Fichier JSON = {json_before_change}."}, 
        {"role": "assistant", "content": f"{json_after_change}"}]}

    final_json = json.dumps(template, indent=4)

    return final_json

# Test sur un rapport
prompt = """Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI et leur fichier JSON. 
Ton role est de modifier le fichier JSON du rapport fourni selon les instructions fournies par l'utilisateur.
Tu ne dois pas faire d'autres modifications que celles precisees par l'utilisateur.
Tu dois absolument respecter le schema du JSON fourni dans le fichier JSON que tu reponds.
Si tu ne sais pas comment modifier le fichier JSON, reponds 'Impossible de modifier le fichier JSON'""".replace('\n', '')

instructions = "Ajoute un histogramme du nombre de user_id par pays"
json_path_before_change = "jsons_train/rapport_original.json"
json_path_after_change = "jsons_train/bar_chart_nb_userid_by_country.json"
processed_json = template_json(instructions, json_path_before_change, json_path_after_change, prompt)
print(processed_json)

# Application sur plusieurs rapports
bdd = pd.read_excel("bdd/bdd_train_unif_filtres.xlsx")

bdd['json_resultat'] = bdd.apply(lambda row: template_json(row['instructions'], row['json_path_before_change'], row['json_path_after_change'], prompt), axis=1)

# On ajoute tous les jsons à un fichier jsonl
with open('bdd/bdd_jsons_train_unif_filtres.jsonl', 'w') as file:
    for item in bdd['json_resultat']:
        json_obj = json.loads(item)
        json.dump(json_obj, file)
        file.write('\n')


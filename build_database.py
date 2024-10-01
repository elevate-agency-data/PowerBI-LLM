import json
import pandas as pd


def template_json(instructions, json_path_before_change, json_path_after_change):
# Fonction pour mettre en forme le prompt avec le json PBI
    with open(json_path_before_change, 'r') as json_data :
        json_before_change = json.load(json_data)
    with open(json_path_after_change, 'r') as json_data :
        json_after_change = json.load(json_data)

    template = {"messages": [
        {"role": "system", "content": "Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI au format pbix. Ton role est de modifier le fichier JSON du rapport fourni selon les instructions fournies par l'utilisateur."}, 
        {"role": "user", "content": f"{instructions} fichier JSON = {json_before_change}."}, 
        {"role": "assistant", "content": json_after_change}]}

    final_json = json.dumps(template, indent=4)

    return final_json

# Test sur un rapport
instructions = "Please add a bar chart of the number of users by country."
json_path_before_change = "jsons/rapport_original.json"
json_path_after_change = "jsons/bar_chart_nb_userid_by_country.json"
processed_json = template_json(instructions, json_path_before_change, json_path_after_change)
print(processed_json)

# Application sur plusieurs rapports
bdd = pd.read_excel("bdd.xlsx")

bdd['json_resultat'] = bdd.apply(lambda row: template_json(row['instructions'], row['json_path_before_change'], row['json_path_after_change']), axis=1)

# On ajoute tous les jsons à un fichier jsonl
with open('bdd_fr.jsonl', 'w') as file:
    for item in bdd['json_resultat']:
        json_obj = json.loads(item)
        json.dump(json_obj, file)
        file.write('\n')


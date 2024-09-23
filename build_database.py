import json
import pandas as pd

def template_json(instructions, json_path_before_change, json_path_after_change):
# Fonction pour mettre en forme le prompt avec le json PBI
    with open(json_path_before_change, 'r') as json_data :
        data_before_change = json.load(json_data)
    with open(json_path_after_change, 'r') as json_data :
        data_after_change = json.load(json_data)

    json_before_change = json.dumps(data_before_change)
    json_after_change = json.dumps(data_after_change)

    template = {"messages": [
        {"role": "system", "content": "You are an experienced Power BI engineer working extensively with Power BI pbix format reports. You are expected to modify the report.json file based on the user description."}, 
        {"role": "user", "content": f"{instructions} JSON file = {json_before_change}."}, 
        {"role": "assistant", "content": f"{json_after_change}"}]}

    final_json = json.dumps(template)

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
        print(item)
        json_obj = json.loads(item)
        print(json_obj)
        json.dump(json_obj, file)
        file.write('\n')

import json

json_path = "jsons/rapport_original.json"
with open(json_path, 'r') as json_data :
    json_reference = json.load(json_data)

json_input_path = "jsons/titre_rapport_it.json"
with open(json_input_path, 'r') as json_data :
    json_input = json.load(json_data)


def compare_json_structure(json_input, json_reference):
    if isinstance(json_input, dict) and isinstance(json_reference, dict):
        # Vérifier que les deux JSONs ont les mêmes clés
        if set(json_input.keys()) != set(json_reference.keys()):
            return False
        
        return True
    



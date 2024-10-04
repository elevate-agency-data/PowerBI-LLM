import json
import jsonschema

def generate_json_schema(data):
    if isinstance(data, dict):
        return {
            "type": "object",
            "properties": {key: generate_json_schema(value) for key, value in data.items()}
        }
    elif isinstance(data, list):
        return {
            "type": "array",
            "items": generate_json_schema(data[0]) if len(data) > 0 else {}
        }
    elif isinstance(data, str):
        return {"type": "string"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif data is None:
        return {"type": "null"}
    else:
        raise ValueError(f"Type de données non supporté: {type(data)}")


def compare_json_structure(json_reponse_path, json_reference_path):
    with open(json_reference_path, 'r') as json_data :
        json_reference = json.load(json_data)

    with open(json_reponse_path, 'r') as json_data :
        json_reponse = json.load(json_data)

    schema_reference = generate_json_schema(json_reference)
    schema_reponse = generate_json_schema(json_reponse)

    schema_reference_str = json.dumps(schema_reference, sort_keys=True)
    schema_reponse_str = json.dumps(schema_reponse, sort_keys=True)
    
    return schema_reference_str == schema_reponse_str


json_reference_path = "jsons_test/IT__web.json"
json_reponse_path = "jsons_test/IT__web_TEST.json"
compare_json_structure(json_reponse_path, json_reference_path)



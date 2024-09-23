import json

instructions = "Please add a bar chart of the number of users by country."
json_path_before_change = "jsons/rapport_original.json"
json_path_after_change = "jsons/bar_chart_nb_userid_by_country.json"


def template_bdd(instructions, json_path_before_change, json_path_after_change):

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



processed_json = template_bdd(instructions, json_path_before_change, json_path_after_change)
print(processed_json)
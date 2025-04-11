import openai
import json

def generate_completion(user_input, function_descriptions):
    """Generate completion using OpenAI API"""
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
        functions=function_descriptions,
        function_call="auto",  # Let the model decide if it needs to call the function
    )
    return completion.choices[0].message if completion.choices else {}

def prepare_arguments_add_read_me(kpis, function_descriptions):
    # Run the function call with the extracted KPI data
    add_read_me_output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"{kpis}"
            }
        ],
        functions=function_descriptions,
        function_call={"name": "add_read_me", "arguments": json.dumps({"kpis": kpis})}
    )
    return add_read_me_output.choices[0].message["function_call"]["arguments"]
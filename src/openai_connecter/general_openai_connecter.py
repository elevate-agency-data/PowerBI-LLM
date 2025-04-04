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
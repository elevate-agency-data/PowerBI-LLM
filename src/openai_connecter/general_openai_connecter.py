import openai
import json

from openai.types.shared.reasoning import Reasoning
import config.config as config

def generate_completion(user_input, function_descriptions, model_name=config.DEFAULT_MODEL, openai_client=None):
    """Generate completion using OpenAI API"""
    completion = openai_client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": user_input}],
        functions=function_descriptions,
        function_call="auto",  # Let the model decide if it needs to call the function
    )
    print(openai_client)
    return completion.choices[0].message if completion.choices else {}

def prepare_arguments_add_read_me(kpis, function_descriptions, language, model_name=config.DEFAULT_MODEL, openai_client=None):

    add_read_me_output = openai_client.chat.completions.create(
        model=model_name,
        #reasoning_effort = "high",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are an assistant that writes concise Power BI documentation in {language}. "
                    f"Always return JSON arguments for the add_read_me function fully translated into {language}."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Here is the dashboard overview you must transform into add_read_me arguments. "
                    f"Make sure every field you generate is written in {language}.\n\n{kpis}"
                ),
            },
        ],
        functions=function_descriptions,
        function_call={"name": "add_read_me", "arguments": json.dumps({"kpis": kpis})}
    )
    return add_read_me_output.choices[0].message.function_call.arguments
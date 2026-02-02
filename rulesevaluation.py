import json
import pandas as pd
import os
#from google.colab import userdata
import google.generativeai as genai

from langchain_groq import ChatGroq
import re

from groq import Groq
#from google.colab import userdata

#import json
base_dir = os.path.dirname(__file__)

def load_json(relpath):
    path = os.path.join(base_dir, relpath)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

mappings = load_json(os.path.join("Input", "Control-mappings.json"))
inputjson = load_json(os.path.join("Input", "data.json"))
rules = load_json(os.path.join("Input", "rules.json"))

GROQ_API_KEY =""

def EvaluateRules_GROQ(data,mappings,rules):
  expected_output_schema = {
    "mappings": {
      "ControlName": "EvaluatedValue"
    },
    "showhide": [
      "ControlNameToHide1",
      "ControlNameToHide2"
    ]
  }

  import json
  schema_json_string = json.dumps(expected_output_schema, indent=2)

  prompt = f"""
Given the following input json, control mappings and rules

source data : {data}
mappings: {mappings}
rules: {rules}

You are a logic engine designed to process business rules and map data from a source JSON to a destination schema.
just return the output in json format and dont send any other additional details.
Inputs:
mappings JSON: Defines the logic for data extraction (conditional if/else statements).
Source Data JSON: The raw data for the current opportunity.
rules JSON: Defines which UI controls should be shown or hidden based on data values.

Task:
Analyze the Source Data JSON against the Rule Mapping JSON and Visibility Rules JSON. Generate a final output in JSON format containing two objects:
mappings: A key-value pair of the control name and its evaluated value.
showhide: A list of control names that should be hidden (where the \"show\" condition was not met).

expected output schema
{schema_json_string}
"""


  llm_Groq = ChatGroq(groq_api_key=GROQ_API_KEY,model_name="groq/compound", temperature=0.0 )
  response = llm_Groq.invoke(prompt)
  return response

res = EvaluateRules_GROQ(inputjson,mappings,rules)

response_data = json.loads(res.content)

# Extract mappings and save to a JSON file
mappings_data = response_data.get("mappings", {})
with open("output_mappings.json", "w") as f:
    json.dump(mappings_data, f, indent=2)
print("Mappings data saved to output_mappings.json")

# Extract showhide and save to a JSON file
showhide_data = response_data.get("showhide", [])
with open("output_showhide.json", "w") as f:
    json.dump(showhide_data, f, indent=2)
print("Show/Hide data saved to output_showhide.json")
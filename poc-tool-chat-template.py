import json

from transformers import AutoTokenizer

import util

MODEL = "function-270m"
SYSTEM_MSG = "You are a model that can do function calling with the following functions"

tools_schema = """
[
  {
    "type": "function",
    "function": {
      "name": "health_save_blood_measurement",
      "description": "Save person blood pressure and cardiac pulse in the medical database. Also compute pulse \
pressure as difference between systolic and diastolic pressures.",
      "parameters": {
        "type": "object",
        "properties": {
          "person": {
            "type": "string",
            "description": "human-readable person name, unique per medical database."
          },
          "systole": {
            "type": "integer",
            "description": "systolic pressure expressed as mmHg (millimeters of mercury)."
          },
          "diastole": {
            "type": "integer",
            "description": "diastolic pressure expressed as mmHg (millimeters of mercury)."
          },
          "pulse": {
            "type": "integer",
            "description": "heart rate expressed in bpm (beats per minute)."
          }
        },
        "required": [
          "person",
          "systole",
          "diastole",
          "pulse"
        ]
      }
    }
  }
]
"""

chat = """
  [
    {
      "role": "developer",
      "content": "You are a model that can do function calling with the following functions"
    },
    {
      "role": "user",
      "content": "Save blood pressure measurement of 124/88 mmHg and heart rate of 75 bpm for Rotaru Iulian."
    },
    {
      "role": "assistant",
      "tool_calls": [
        {
          "type": "function",
          "function": {
            "name": "health_save_blood_measurement",
            "arguments": {
              "person": "Rotaru Iulian",
              "systole": 124,
              "diastole": 88,
              "pulse": 75
            }
          }
        }
      ]
    }
  ]
"""

tools_schema = json.loads(tools_schema)
print()
print(f"tools_schema: {tools_schema}")

chat = json.loads(chat)
print()
print(f"chat: {chat}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
text = tokenizer.apply_chat_template(chat, tools=tools_schema, tokenize=False, add_generation_prompt=False)
print()
print(f"tokenizer text: |{text}|")
print()
print("WARN: Transformers' chat template is buggy. It does not preserve arguments order.")

print()
print("Monkey patch on tokenizer.apply_chat_template for tool argument order.")
util.patch_tokenizer(tokenizer)
text = tokenizer.apply_chat_template(chat, tools=tools_schema, tokenize=False, add_generation_prompt=False)
print()
print(f"custom text: |{text}|")
print()
print("INFO: Custom tool processing correctly preserve arguments order.")

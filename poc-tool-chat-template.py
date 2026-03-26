import json

from transformers import AutoTokenizer

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
              "pulse": 77
            }
          }
        }
      ]
    }
  ]
"""


def escape(value):
    return f"<escape>{value}<escape>" if isinstance(value, str) else value


def encode_tools_schema(tools):
    response = ""
    for tool in tools:
        function = tool['function']

        properties = []
        required = []
        if 'parameters' in function and 'properties' in function['parameters']:
            for k, v in function['parameters']['properties'].items():
                p = f"{k}:{{description:{escape(v['description'])},type:{escape(v['type'].upper())}}}"
                properties.append(p)
                required.append(escape(k))
        parameters = f"properties:{{{','.join(properties)}}},required:[{','.join(required)}],type:{escape('OBJECT')}"

        declaration = f"declaration:{function['name']}"
        description = escape(function['description'])
        body = f"description:{description},parameters:{{{parameters}}}"
        response += f"<start_function_declaration>{declaration}{{{body}}}<end_function_declaration>"
    return response


def encode_tools_call(tool_calls):
    response = ""
    for tool_call in tool_calls:
        function = tool_call['function']
        arguments = ",".join([f"{k}:{escape(v)}" for k, v in function['arguments'].items()])
        response += f"<start_function_call>call:{function['name']}{{{arguments}}}<end_function_call>"
    return response


def apply_chat_template(conversation: list[dict[str, str]], tools: list[dict] = None, tokenize: bool = False) -> str:
    for turn in conversation:
        if turn['role'] == "developer":
            if tools:
                turn['content'] += encode_tools_schema(tools)
                tools = None
            continue

        if turn['role'] == "assistant":
            tool_calls = turn.pop('tool_calls', None)
            if tool_calls:
                turn['content'] = encode_tools_call(tool_calls)

    return tokenizer.apply_chat_template(conversation, tools, tokenize=tokenize)


tools_schema = json.loads(tools_schema)
print()
print(f"tools_schema: {tools_schema}")

chat = json.loads(chat)
print()
print(f"chat: {chat}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
text = tokenizer.apply_chat_template(chat, tools=tools_schema, tokenize=False)
print()
print(f"tokenizer text: {text}")
print()
print("WARN: Transformers' chat template is buggy. It does not preserve arguments order.")

text = apply_chat_template(chat, tools=tools_schema, tokenize=False)
print()
print(f"custom text: {text}")
print()
print("INFO: Custom tool processing correctly preserve arguments order.")

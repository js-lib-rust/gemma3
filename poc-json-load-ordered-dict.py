from collections import OrderedDict
import json

dataset = """[
  {"role": "system", "content": "You are a model that can do function calling with the following functions"},
  {"role": "user", "content": "TV remote control seems not working. Please analyse."},
  {"role": "model", "tool_calls": [{"type": "function", "function": {"name": "run_device_diagnose", "arguments": {"device":"TV remote control","level":1}}}]}
]"""

conversation = json.loads(dataset, object_hook=OrderedDict)
print(conversation)

model_turn = [turn for turn in conversation if turn['role'] == 'model'][0]
print(json.dumps(model_turn['tool_calls'][0]['function']['arguments']))


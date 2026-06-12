import time

from transformers import AutoTokenizer
import requests
import json
import util

URL = "http://jarvis.local:8888/v1/chat/completions"
MODEL = "function-270m"
TOOL = "data/tool/hera.tools.hf.json"

with open(TOOL, 'r') as file:
    tools_schema = json.load(file)

chat = """
  [
    {
      "role": "developer",
      "content": "You are a model that can do function calling with the following functions"
    },
    {
      "role": "user",
      "content": "Turn off the central heating."
    }
  ]
"""
chat = json.loads(chat)

tokenizer = AutoTokenizer.from_pretrained(MODEL)
util.patch_tokenizer(tokenizer)
text = tokenizer.apply_chat_template(chat, tools=tools_schema, tokenize=False, add_generation_prompt=True)

print(f"|{text}|")

request = {
    "model": "function-270m.gguf",
    "messages": [{
        "role": "user",
        "content": text
    }],
    "temperature": 0,
    "stream": False,
    "stop": ["<end_function_call>"]
}
print(f"request: {request}")

json_data = json.dumps(request).encode('utf-8')
headers = {'Content-Type': 'application/json'}
session = requests.session()
for _ in range(10):
    start = time.time()
    response = session.post(URL, data=json_data, headers=headers)
    print()
    print(response.json())
    print()
    print(f"Processing time: {time.time() - start}")

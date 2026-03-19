import time

import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, TextStreamer, AutoProcessor
import json
import util

MODEL = "/functiongemma-270m-it"
# MODEL = "function-270m"
SYSTEM_MSG = "You are a model that can do function calling with the following functions"


def create_conversation(sample):
    return {
        "messages": [
            {"role": "developer", "content": SYSTEM_MSG},
            {"role": "user", "content": sample["user_content"]},
            {"role": "assistant", "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": sample["tool_name"],
                        "arguments": json.loads(sample["tool_arguments"])
                    }
                }
            ]
             },
        ],
        "tools": tools
    }


device = "cuda:0" if torch.cuda.is_available() else "cpu"
model_path = util.get_model_path(MODEL) if MODEL.startswith('/') else MODEL
# model_path = "google/functiongemma-270m-it"

processor = AutoProcessor.from_pretrained(model_path)
processor.pad_token = processor.eos_token
setattr(processor, "parse_response", util.parse_gemma_function_response)
print(f"Processor loaded from {model_path} on {device}")

model = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16)
model.to(device)
model.eval()
print(f"Model loaded from {model_path} on {device}")

with open("data/function/poc-function-schema.json", 'r', encoding='UTF-8') as file:
    tools = json.load(file)
print()
print("tools:")
[print(f"- {tool}") for tool in tools]

with open("data/function/poc-function-set.jsonl", 'r', encoding='UTF-8') as file:
    function_list = [json.loads(line) for line in file if line.strip()]
dataset = Dataset.from_list(function_list)
dataset = dataset.map(create_conversation)
print()
print(f"messages: {dataset['messages'][0]}")

text = processor.apply_chat_template(dataset['messages'][0], tools=tools, tokenize=False)
print(text)

text = """<bos><start_of_turn>developer
You are a model that can do function calling with the following functions\
<start_function_declaration>declaration:search_knowledge_base{\
description:<escape>Search internal company documents, policies and project data.<escape>,\
parameters:{properties:{query:{description:<escape>query string<escape>,type:<escape>STRING<escape>}},\
required:[<escape>query<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration>\
<start_function_declaration>declaration:search_google{\
description:<escape>Search public information.<escape>,\
parameters:{properties:{query:{description:<escape>query string<escape>,type:<escape>STRING<escape>}},\
required:[<escape>query<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration><end_of_turn>
<start_of_turn>user
What is the reimbursement limit for travel meals?<end_of_turn>
<start_of_turn>model
"""

streamer = TextStreamer(processor)
config = {
    'max_new_tokens': 100,
    'do_sample': False,
    'num_beams': 1,
    'num_return_sequences': 1,
    'pad_token_id': processor.eos_token_id,
    'streamer': None
}

print()
print("Generating function call")
start_time = time.time()
inputs = processor(text, return_tensors="pt", truncation=True, max_length=1000)
inputs = {k: v.to(device) for k, v in inputs.items()}
with torch.no_grad():
    outputs = model.generate(**inputs, **config)
    if not config['streamer']:
        input_length = inputs["input_ids"].shape[1]
        for output in outputs:
            function_call_response = processor.decode(output[input_length:], skip_special_tokens=True)
print(f"Function call generation processing time {time.time() - start_time} sec.")

print(f"function_call_response: {function_call_response}")
print(f"function_call: {processor.parse_response(function_call_response)}")

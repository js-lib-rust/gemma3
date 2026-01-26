from transformers import AutoTokenizer
from transformers.utils import get_json_schema
from datasets import Dataset
import json

MODEL = "function-270m"
SYSTEM_MSG = "You are a model that can do function calling with the following functions"


def create_conversation(sample):
    return {
        "messages": [
            {"role": "developer", "content": SYSTEM_MSG},
            {"role": "user", "content": sample["user_content"]},
            {"role": "assistant", "tool_calls": [{"type": "function", "function": {"name": sample["tool_name"],
                                                                                   "arguments": json.loads(
                                                                                       sample["tool_arguments"])}}]},
        ],
        "tools": tools
    }


with open("data/poc-function-schema.json", 'r', encoding='UTF-8') as file:
    tools = json.load(file)
print(f"tools: {tools}")

with open("data/poc-function-set.jsonl", 'r', encoding='UTF-8') as file:
    function_list = [json.loads(line) for line in file if line.strip()]
dataset = Dataset.from_list(function_list)
dataset = dataset.map(create_conversation, remove_columns=dataset.features)
print(f"messages: {dataset['messages']}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
text = tokenizer.apply_chat_template(chat=dataset['messages'], tools=tools, tokenize=False)
print(text)

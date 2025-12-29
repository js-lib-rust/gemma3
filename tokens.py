import yaml
from transformers import AutoTokenizer
import os

MODEL_DIR = os.environ.get("AI_MODEL_DIR")
MODEL_NAME = MODEL_DIR + "/hugging-face/model/gemma-3-1b-it"
YAML_FILE = "data/formatter-set.yml"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
tokenizer.truncation_side = "right"

with open(YAML_FILE, 'r', encoding='utf-8') as f:
    dataset = yaml.safe_load(f)

dataset_size = len(dataset)
max_tokens = 0
for index, datapoint in enumerate(dataset):
    chat = datapoint['messages']
    chat_text = tokenizer.apply_chat_template(chat, tokenize=False)
    chat_tokens = tokenizer(chat_text)
    chat_tokens_count = len(chat_tokens['input_ids'])
    print(f"{index + 1:>3} / {dataset_size}: {chat_tokens_count}")
    if max_tokens < chat_tokens_count:
        max_tokens = chat_tokens_count

print()
print(f"max_tokens: {max_tokens}")

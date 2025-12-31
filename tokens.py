import yaml
from transformers import AutoTokenizer
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--model", action="store")
parser.add_argument("--file", action="store")
args = parser.parse_args()

MODEL_DIR = os.environ.get("AI_MODEL_DIR")
DEFAULT_MODEL = "gemma-3-1b-it"
DEFAULT_FILE = "formatter-set"

model_name = args.model if args.model else DEFAULT_MODEL
model_path = f"{MODEL_DIR}/hugging-face/model/{model_name}"
file_name = args.file if args.file else DEFAULT_FILE
file_path = f"data/{file_name}.yml"
if args.verbose:
    print(f"Use model {model_path}")
    print(f"Use file {file_path}")

tokenizer = AutoTokenizer.from_pretrained(model_path)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
tokenizer.truncation_side = "right"

if args.verbose:
    print(f"Loading dataset {file_path} ...")
with open(file_path, 'r', encoding='utf-8') as file:
    dataset = yaml.safe_load(file)
if args.verbose:
    print(f"Loaded {len(dataset)} examples")
    print()

dataset_size = len(dataset)
max_tokens = 0
for index, datapoint in enumerate(dataset):
    chat = datapoint['chat']
    chat_text = tokenizer.apply_chat_template(chat, tokenize=False)
    chat_tokens = tokenizer(chat_text)
    chat_tokens_count = len(chat_tokens['input_ids'])
    if args.verbose:
        print(f"{index + 1:>3} / {dataset_size}: {chat_tokens_count}")
    if max_tokens < chat_tokens_count:
        max_tokens = chat_tokens_count

if args.verbose:
    print()
print(f"max_tokens: {max_tokens}")

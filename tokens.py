import yaml
from transformers import AutoTokenizer
import os
import argparse
import util

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--model", action="store")
parser.add_argument("--files", action="store", type=util.split_by_comma)
args = parser.parse_args()

MODEL_DIR = os.environ.get("AI_MODEL_DIR")
DEFAULT_MODEL = "gemma-3-270m-it"

model_name = args.model if args.model else DEFAULT_MODEL
model_path = f"{MODEL_DIR}/hugging-face/model/{model_name}"
print()
print(f"Use model {model_path}")
print(f"Use files {args.files}")
print()

tokenizer = AutoTokenizer.from_pretrained(model_path)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
tokenizer.truncation_side = "right"

total_tokens = 0
max_tokens = 0

for file_name in args.files:
    file_path = f"data/{file_name}.yml"
    file_tokens = 0
    if os.path.exists(file_path):
        print(f"Loading instruction dataset {file_path} ...")
        with open(file_path, 'r', encoding='utf-8') as file:
            dataset = yaml.safe_load(file)
        dataset_size = len(dataset)
        print(f"Loaded {dataset_size} instruction examples")

        for index, datapoint in enumerate(dataset):
            chat = datapoint['chat']
            chat_text = tokenizer.apply_chat_template(chat, tokenize=False)
            tokens = tokenizer(chat_text)
            tokens_count = len(tokens['input_ids'])
            if args.verbose:
                print(f"{index + 1:>3} / {dataset_size}: {tokens_count}")

            total_tokens += tokens_count
            if max_tokens < tokens_count:
                max_tokens = tokens_count
            file_tokens += tokens_count
        print(f"Processed {file_tokens} instruction tokens")
        print()

    file_path = f"data/{file_name}.md"
    file_tokens = 0
    if os.path.exists(file_path):
        print(f"Loading domain dataset {file_path} ...")
        with open(file_path, 'r', encoding='utf-8') as file:
            dataset = [line.strip() for line in file]
        dataset_size = len(dataset)
        print(f"Loaded {dataset_size} domain examples")

        for index, datapoint in enumerate(dataset):
            tokens = tokenizer(datapoint)
            tokens_count = len(tokens['input_ids'])
            if args.verbose:
                print(f"{index + 1:>3} / {dataset_size}: {tokens_count}")

            total_tokens += tokens_count
            if max_tokens < tokens_count:
                max_tokens = tokens_count
            file_tokens += tokens_count
        print(f"Processed {file_tokens} domain tokens")
        print()

print()
print(f"total_tokens: {total_tokens}")
print(f"max_tokens: {max_tokens}")

import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--model", action="store", type=str, required=True)
args = parser.parse_args()

model = args.model
tokenizer_path = f"{model}/tokenizer.json" 

with open(tokenizer_path, 'r') as f:
    vocab_json = json.load(f)

vocab = vocab_json['model']['vocab']
max_id = max(vocab.values())
vocab_size = max_id + 1

print(f"Vocabulary size for model {model} is: {vocab_size}")

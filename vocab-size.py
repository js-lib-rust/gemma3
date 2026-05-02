import argparse
import json
import util

parser = argparse.ArgumentParser()
parser.add_argument("--model", action="store", type=str, required=True)
args = parser.parse_args()

model_path = util.get_model_path(args.model) if args.model.startswith('/') else args.model
print(f"Use model path {model_path}")

tokenizer_path = f"{model_path}/tokenizer.json"

with open(tokenizer_path, 'r', encoding='UTF-8') as f:
    vocab_json = json.load(f)

vocab = vocab_json['model']['vocab']
max_id = max(vocab.values())
vocab_size = max_id + 1

print(f"Vocabulary size for model {model_path} is: {vocab_size}")

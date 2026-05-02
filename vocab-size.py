import json

model = "router-270m"
tokenizer_path = f"{model}/tokenizer.json" 

with open(tokenizer_path, 'r') as f:
    data = json.load(f)

vocab = data['model']['vocab']
max_id = max(vocab.values())
vocab_size = max_id + 1

print(f"Vocabular size for model {model} is: {vocab_size}")


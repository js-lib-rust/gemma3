import argparse
import time
import os
import numpy as np
import torch
import yaml
import evaluate
from transformers import AutoTokenizer, AutoModelForCausalLM
import util

BASE_MODEL = util.get_model_path("gemma-3-270m-it")
EVAL_MODEL = "formatter-270m"
DATA_FILE = ["medical-response-eval", "hera-response-eval", "weather-response-eval"]
ROUGE = evaluate.load("rouge")
BERT = evaluate.load("bertscore")

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--model", action="store")
parser.add_argument("--list", action="store_true")
parser.add_argument("--use-base-model", action="store_true")
parser.add_argument("--files", type=util.split_by_comma, action="store")
parser.add_argument("--max-new-tokens", type=int, action="store", default="2000")
parser.add_argument("tests", type=int, nargs='*', help="tests number to execute")
args = parser.parse_args()

model_name = args.model if args.model else EVAL_MODEL
model_path = BASE_MODEL if args.use_base_model else model_name
print(f"Use model `{model_path}`.")
print(f"Use max new tokens {args.max_new_tokens}.")

data_files = args.files if args.files else DATA_FILE
dataset = []
for data_file in data_files:
    data_file = f"data/{data_file}.yml"
    with open(data_file, 'r', encoding='UTF-8') as file:
        fileset = yaml.safe_load(file)
        print(f"Loaded {len(fileset)} tests from the file `{os.path.abspath(data_file)}`.")
        dataset += fileset

if args.list:
    for index, datapoint in enumerate(dataset):
        print(f"{index + 1:>3}. {util.get_chat_prompt(datapoint['chat'])}")
    exit(0)

if args.tests:
    dataset = [dataset[test - 1] for test in args.tests]
print()
print(f"Running {len(dataset)} tests ...")

device = "cuda" if torch.cuda.is_available() else "cpu"
eval_tokenizer = AutoTokenizer.from_pretrained(model_path)
eval_tokenizer.pad_token = eval_tokenizer.eos_token
eval_model = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16, device_map=device)
eval_model.eval()

config = {
    'max_new_tokens': args.max_new_tokens,
    'do_sample': False,
    'pad_token_id': eval_tokenizer.eos_token_id,
}

similarity_scores = []
dataset_size = len(dataset)
start_time = time.time()
for index, datapoint in enumerate(dataset):
    chat = datapoint['chat']
    prompt = util.get_chat_prompt(chat)
    ground_truth = datapoint['ground_truth']

    input_text = eval_tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = eval_tokenizer(input_text, return_tensors="pt", truncation=True, max_length=4000)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = eval_model.generate(**inputs, **config)
    input_length = inputs["input_ids"].shape[1]
    prediction = eval_tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    similarity_score = util.get_similarity_score(prediction, ground_truth)
    similarity_scores.append(similarity_score)
    print(f"{index + 1:>3} / {dataset_size}: {similarity_score:>7.4f}: {prompt}")

    if args.verbose:
        print(prediction)

print()
mean_score = np.mean(similarity_scores)
median_score = np.median(similarity_scores)
print(f"Mean Similarity Score: {mean_score:.4f}")
print(f"Median Similarity Score: {median_score:.4f}")

print()
std_dev = np.std(similarity_scores)
print(f"Standard Deviation: {std_dev:.4f}")

print()
min_score = np.min(similarity_scores)
max_score = np.max(similarity_scores)
print(f"Minimum Similarity Score: {min_score:.4f}")
print(f"Maximum Similarity Score: {max_score:.4f}")

print()
percentile_25 = np.percentile(similarity_scores, 25)
percentile_75 = np.percentile(similarity_scores, 75)
print(f"25th Percentile: {percentile_25:.4f}")
print(f"75th Percentile: {percentile_75:.4f}")

print()
elapsed_time = time.time() - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")

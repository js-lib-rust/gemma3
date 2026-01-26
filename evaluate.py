import argparse
import time
import os
import numpy as np
import torch
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
import util

BASE_MODEL = util.get_model_path("gemma-3-270m-it")
EVAL_MODEL = "formatter-270m"
DATA_FILE = ["medical-response-eval", "hera-response-eval", "weather-response-eval"]

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--trace", action="store_true")
parser.add_argument("--model", action="store")
parser.add_argument("--list", action="store_true")
parser.add_argument("--use-base-model", action="store_true")
parser.add_argument("--files", action="store", type=util.split_by_comma)
parser.add_argument("--tools", action="store", type=util.split_by_comma)
parser.add_argument("--inject-tools", action="store_true")
parser.add_argument("--max-new-tokens", action="store", type=int, default="2000")
parser.add_argument("tests", nargs='*', type=int, help="tests number to execute")
args = parser.parse_args()

model_name = args.model if args.model else EVAL_MODEL
model_path = BASE_MODEL if args.use_base_model else model_name
print(f"Use verbose {args.verbose}")
print(f"Use trace {args.trace}")
print(f"Use model `{model_path}`.")
print(f"Use files {args.files}")
print(f"Use tools {args.tools}")
print(f"Use inject tools {args.inject_tools}")
print(f"Use max new tokens {args.max_new_tokens}.")

data_files = args.files if args.files else DATA_FILE
dataset = []
for data_file in data_files:
    data_file = f"data/{data_file}"
    with open(data_file, 'r', encoding='UTF-8') as file:
        fileset = json.load(file)
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

if args.tools:
    tools = []
    for file_name in args.tools:
        with open(f"data/{file_name}", 'r', encoding='UTF-8') as file:
            tools += json.load(file)
else:
    tools = None

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16, device_map=device)
model.resize_token_embeddings(len(tokenizer))
model.eval()

config = {
    'max_new_tokens': args.max_new_tokens,
    'do_sample': False,
    'pad_token_id': tokenizer.eos_token_id,
}

similarity_scores = []
dataset_size = len(dataset)
start_time = time.time()
for index, datapoint in enumerate(dataset):
    if args.inject_tools:
        util.inject_tools(tools, datapoint)
    ground_truth = datapoint.pop()['content']
    conversation = datapoint
    prompt = util.get_chat_prompt(conversation)

    input_text = tokenizer.apply_chat_template(conversation, tools=tools, tokenize=False, add_generation_prompt=True)
    if args.trace:
        print(f"input_text: {input_text}")
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=1000)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(**inputs, **config)
    input_length = inputs["input_ids"].shape[1]
    prediction = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    similarity_score = util.get_similarity_score(prediction, ground_truth)
    similarity_scores.append(similarity_score)
    print(f"{index + 1:>3} / {dataset_size}: {time.time() - start_time:>4.2f} sec: {similarity_score:>7.4f}: {prompt}")

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

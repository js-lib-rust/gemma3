import os
import argparse
import yaml
import util

parser = argparse.ArgumentParser()
parser.add_argument("--files", action="store", type=util.split_by_comma)
args = parser.parse_args()

print(f"Use files {args.files}")

for file_name in args.files:
    file_path = f"data/{file_name}.yml"
    if not os.path.exists(file_path):
        continue
    print()

    print(f"Loading instruction dataset {file_path} ...")
    with open(file_path, 'r', encoding='UTF-8') as file:
        dataset = yaml.safe_load(file)
    dataset_size = len(dataset)
    print(f"Loaded {dataset_size} instruction examples")

    for index, datapoint in enumerate(dataset):
        chat = datapoint['chat']
        prompt = util.get_chat_prompt(chat)
        print(f"{index:<2}: {prompt}")

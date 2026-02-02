import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--task", action="store", default="gemma_function_format")
parser.add_argument("--file", action="store")
parser.add_argument("--use-function-model", action="store_true")
args = parser.parse_args()

print(f"Use task {args.task}")
print(f"Use file {args.file}")
print()


def gemma_function_format():
    file_path = f"data/{args.file}"
    with open(file_path, 'r', encoding='UTF-8') as file:
        functions = json.load(file)

    for function_name, function_descriptor in functions.items():
        # <start_function_declaration>declaration:hera_list_devices{description:<escape>List all devices registered to HERA<escape>,parameters:{type:<escape>OBJECT<escape>,properties:{},required:[]}}<end_function_declaration>

        parameters_type = function_descriptor['parameters']['type']
        properties = function_descriptor['parameters']['properties']
        required = function_descriptor['parameters']['required']

        description = f"<escape>{function_descriptor['description']}<escape>"
        parameters = f"{{type:<escape>{parameters_type}<escape>,properties:{{"
        for property_name, property_descriptor in properties.items():
            parameters += f"{property_name}:{{"
            parameters += f"type:<escape>{property_descriptor['type']}<escape>"
            parameters += f",description:<escape>{property_descriptor['description']}<escape>"
            if "enum" in property_descriptor:
                parameters += f",enum:["
                parameters += ",".join([f"<escape>{item}<escape>" for item in property_descriptor['enum']])
                parameters += "]"
            parameters += "}"
        parameters += "},required:["
        parameters += ",".join([f"<escape>{item}<escape>" for item in required])
        parameters += "]}"

        declaration = f"<start_function_declaration>declaration:{function_name}{{description:{description},parameters:{parameters}}}<end_function_declaration>"
        print(declaration)


def hf_function_set():
    file_path = f"data/{args.file}"
    with open(file_path, 'r', encoding='UTF-8') as file:
        dataset = [json.loads(line) for line in file if line.strip()]

    system_role = "developer" if args.use_function_model else "system"
    model_role = "assistant" if args.use_function_model else "model"
    hf_dataset = []
    for sample in dataset:
        hf_sample = f"""  [
    {{"role": "{system_role}", "content": "You are a model that can do function calling with the following functions"}},
    {{"role": "user", "content": "{sample["prompt"]}"}},
    {{"role": "{model_role}", "tool_calls": [{{"type": "function", "function": {{"name": "{sample["function"]}", "arguments": {sample["arguments"]}}}}}]}}
  ]"""
        hf_dataset.append(hf_sample)
    sample_separator = ",\n"
    print(f"[\n{sample_separator.join(hf_dataset)}\n]")


def hf_rewrite_set():
    file_path = f"data/{args.file}"
    with open(file_path, 'r', encoding='UTF-8') as file:
        dataset = [json.loads(line) for line in file if line.strip()]

    hf_dataset = []
    for sample in dataset:
        hf_sample = f"""  [
    {{"role": "system", "content": "Classify and rewrite next user prompt"}},
    {{"role": "user", "content": "{sample["user"]}"}},
    {{"role": "model", "content": "{sample['agent'].lower()}: {sample['prompt']}"}}
  ]"""
        hf_dataset.append(hf_sample)
    sample_separator = ",\n"
    print(f"[\n{sample_separator.join(hf_dataset)}\n]")


module = __import__(__name__)
function = getattr(module, args.task)
function()

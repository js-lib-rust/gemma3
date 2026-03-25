import argparse
import json
import schema

parser = argparse.ArgumentParser()
parser.add_argument("--task", action="store", default="gemma_function_format")
parser.add_argument("--file", action="store")
parser.add_argument("--tool", action="store")
parser.add_argument("--use-function-model", action="store_true")
args = parser.parse_args()

print(f"Use task {args.task}")
print(f"Use file {args.file}")
print(f"Use tool {args.tool}")
print()


def gemma_function_format():
    file_path = f"data/{args.file}"
    with open(file_path, 'r', encoding='UTF-8') as file:
        functions = json.load(file)

    for function_name, function_descriptor in functions.items():
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

        declaration = (f"<start_function_declaration>declaration:{function_name}{{description:{description},"
                       f"parameters:{parameters}}}<end_function_declaration>")
        print(declaration)


def hf_tool_schema():
    file_path = f"data/{args.file}"
    with open(file_path, 'w', encoding='UTF-8') as file:
        json.dump(schema.get(args.tool), file, indent=2, ensure_ascii=False)


def hf_function_set():
    file_path = f"data/{args.file}"
    dataset = []
    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('--'):
                # print(f"line: {line}")
                sample = json.loads(line)
                # print(sample)
                dataset.append(sample)

    system_role = "developer" if args.use_function_model else "system"
    model_role = "assistant" if args.use_function_model else "model"
    hf_dataset = []
    for sample in dataset:
        hf_sample = [
            {"role": system_role,
             "content": "You are a model that can do function calling with the following functions"},
            {"role": "user", "content": sample['prompt']},
            {"role": model_role,
             "tool_calls": [{"type": "function", "function": {"name": sample['function'],
                                                              "arguments": sample['arguments']}}]}
        ]
        hf_dataset.append(hf_sample)
    print(json.dumps(hf_dataset, indent=2, ensure_ascii=False))


def hf_router_set():
    file_path = f"data/{args.file}"
    dataset = []
    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('--'):
                # print(f"line: {line}")
                sample = json.loads(line)
                # print(sample)
                dataset.append(sample)

    hf_dataset = []
    for sample in dataset:
        turns = [{"role": "system", "content": "Route and rewrite the next user prompt"}]
        for turn in sample:
            turns.append({"role": "user", "content": turn["user"]})
            turns.append({"role": "model", "content": turn['model']})
        hf_dataset.append(turns)
    print(json.dumps(hf_dataset, indent=2))


def escape(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("\"", "\\\"")
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\t", "\\t")
    return s


module = __import__(__name__)
function = getattr(module, args.task)
function()

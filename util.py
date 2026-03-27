import json
import os
import re

import torch
from sentence_transformers import util, SentenceTransformer
from transformers import AutoTokenizer, TokenizersBackend


def get_model_path(model_name):
    if model_name.startswith('/'):
        model_name = model_name[1:]
    model_path = os.environ.get("AI_MODEL_DIR").replace('\\', '/') + "/hugging-face/model/" + model_name
    if not os.path.exists(model_path):
        raise Exception(f"Model path {model_path} not found.")
    return model_path


PROMPT_TAG = "User Prompt: "
SCORE_MODEL = SentenceTransformer(get_model_path("all-MiniLM-L6-v2"))


def get_chat_prompt(chat_arg):
    content = next((item['content'] for item in chat_arg if item['role'] == 'user'), None)
    prompt_tag_index = content.find(PROMPT_TAG)
    if prompt_tag_index == -1:
        return content.splitlines()[0]
    return content[prompt_tag_index + len(PROMPT_TAG):].strip()


def get_similarity_score(prediction_arg, ground_truth_arg):
    if not isinstance(ground_truth_arg, str):
        ground_truth_arg = str(ground_truth_arg)
    prediction_embedding = SCORE_MODEL.encode(prediction_arg, convert_to_tensor=True)
    ground_truth_embedding = SCORE_MODEL.encode(ground_truth_arg, convert_to_tensor=True)
    return util.cos_sim(prediction_embedding, ground_truth_embedding).item()


def split_by_comma(text_arg):
    values = text_arg.split(',')
    return [v.strip() for v in values]


def dtype(dtype_arg):
    if dtype_arg == 'bfloat16':
        return torch.bfloat16
    return torch.float32


def inject_tools(tools, conversation, model_training=False):
    system_turn = [turn for turn in conversation if turn['role'] == "system"][0]
    functions = "\n".join([json.dumps(function) for function in tools])
    system_turn['content'] += f"\n\n{functions}"

    user_turn = [turn for turn in conversation if turn['role'] == "user"][0]
    user_turn['content'] = f"User Prompt: {user_turn['content']}"

    if model_training:
        model_turn = [turn for turn in conversation if turn['role'] == "model"][0]
        model_turn['content'] = json.dumps(model_turn['tool_calls'][0]['function'])
        del model_turn['tool_calls']


def parse_function_call(model_family, hf_function_call):
    parser = FUNCTION_CALL_PARSERS.get(model_family)
    if not parser:
        return json.dumps(hf_function_call)
    return parser(hf_function_call)


def gemma_function_call_parser(hf_function_call):
    function = hf_function_call['name']
    arguments = hf_function_call['arguments']
    arguments = "\n".join([f"{k}:<escape>{v}<escape>" for k, v in arguments.items()])
    return f"<start_function_call>call:{function}{{{arguments}}}<end_function_call>"


FUNCTION_CALL_PARSERS = {
    'gemma': gemma_function_call_parser
}
TOOLS_KEYWORDS = ["tool_call", "function_call", "tools", "tool_choice", "function", "json"]


def has_tools_support(tokenizer):
    if not tokenizer.chat_template:
        return False
    for tools_keyword in TOOLS_KEYWORDS:
        if tools_keyword in tokenizer.chat_template.lower():
            return True
    return False


def template(file_name, variables):
    with open(f"data/template/{file_name}.txt", 'r', encoding='UTF-8') as file:
        text = file.read()
    for key, value in variables.items():
        text = text.replace('{' + key + '}', value)
    return text


def parse_gemma_function_response(text):
    def cast(v):
        try:
            return int(v)
        except:
            try:
                return float(v)
            except:
                return {'true': True, 'false': False}.get(v.lower(), v.strip("'\""))

    return [{
        "name": name,
        "arguments": {
            k: cast((v1 or v2).strip())
            for k, v1, v2 in re.findall(r"(\w+):(?:<escape>(.*?)<escape>|([^,}]*))", args)
        }
    } for name, args in re.findall(r"<start_function_call>call:(\w+)\{(.*?)}<end_function_call>", text, re.DOTALL)]


# ---------------------------------------------------------
# Monkey patch for tokenizer.apply_chat_template for tool argument order.

def escape(value):
    return f"<escape>{value}<escape>" if isinstance(value, str) else value


def encode_tools_schema(tools):
    response = ""
    for tool in tools:
        function = tool['function']

        properties = []
        required = []
        if 'parameters' in function and 'properties' in function['parameters']:
            for k, v in function['parameters']['properties'].items():
                p = f"{k}:{{description:{escape(v['description'])},type:{escape(v['type'].upper())}}}"
                properties.append(p)
                required.append(escape(k))
        parameters = f"properties:{{{','.join(properties)}}},required:[{','.join(required)}],type:{escape('OBJECT')}"

        declaration = f"declaration:{function['name']}"
        body = f"description:{escape(function['description'])},parameters:{{{parameters}}}"
        response += f"<start_function_declaration>{declaration}{{{body}}}<end_function_declaration>"
    return response


def encode_tools_call(tool_calls):
    response = ""
    for tool_call in tool_calls:
        function = tool_call['function']
        arguments = ",".join([f"{k}:{escape(v)}" for k, v in function['arguments'].items()])
        response += f"<start_function_call>call:{function['name']}{{{arguments}}}<end_function_call>"
    return response


tokenizer: TokenizersBackend


def patch_tokenizer(stock_tokenizer: TokenizersBackend) -> None:
    assert hasattr(stock_tokenizer, "apply_chat_template")
    global tokenizer
    tokenizer = stock_tokenizer
    setattr(tokenizer, "__apply_chat_template__", tokenizer.apply_chat_template)
    setattr(tokenizer, "apply_chat_template", _apply_chat_template)


def _apply_chat_template(
        conversation: list[dict[str, str]],
        tools: list[dict] = None,
        tokenize: bool = False,
        add_generation_prompt: bool = False) -> str:
    """
    When applying a chat template, the Transformers library does not preserve the original order of tool arguments — it
    appears to sort them alphabetically by name.

    This patch replaces only tool processing from tokenizer apply_chat_template then invoke original library method,
    but with tools processing disabled. It actually uses library method only for instruction turns.

    All arguments and return type are similar to library method.
    :param conversation:
    :param tools:
    :param tokenize:
    :param add_generation_prompt:
    :return:
    """

    for turn in conversation:
        if turn['role'] == "developer":
            if tools:
                turn['content'] += encode_tools_schema(tools)
                tools = None
            continue

        if turn['role'] == "assistant":
            tool_calls = turn.pop('tool_calls', None)
            if tool_calls:
                turn['content'] = encode_tools_call(tool_calls)

    return tokenizer.__apply_chat_template__(conversation, tools, tokenize=tokenize,
                                             add_generation_prompt=add_generation_prompt)

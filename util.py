import os
import json

import torch
from sentence_transformers import util, SentenceTransformer
from torch import bfloat16


def get_model_path(model_name):
    if model_name.startswith('/'):
        model_name = model_name[1:]
    return os.environ.get("AI_MODEL_DIR") + "/hugging-face/model/" + model_name


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

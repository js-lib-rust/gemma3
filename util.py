import os
import json

from sentence_transformers import util, SentenceTransformer


def get_model_path(model_name):
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


def inject_tools(tools, conversation):
    system_turn = [turn for turn in conversation if turn['role'] == "system"][0]
    functions = "\n".join([json.dumps(function) for function in tools])
    system_turn['content'] += f"\n\n{functions}"

    user_turn = [turn for turn in conversation if turn['role'] == "user"][0]
    user_turn['content'] = f"User Prompt: {user_turn['content']}"

    model_turn = [turn for turn in conversation if turn['role'] == "model"][0]
    model_turn['content'] = json.dumps(model_turn['tool_calls'][0]['function'])
    del model_turn['tool_calls']

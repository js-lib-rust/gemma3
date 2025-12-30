import os

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
    prediction_embedding = SCORE_MODEL.encode(prediction_arg, convert_to_tensor=True)
    ground_truth_embedding = SCORE_MODEL.encode(ground_truth_arg, convert_to_tensor=True)
    return util.cos_sim(prediction_embedding, ground_truth_embedding).item()

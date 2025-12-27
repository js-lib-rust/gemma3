import argparse

from sentence_transformers import util, SentenceTransformer
import os


def get_model_path(model_name):
    return os.environ.get("AI_MODEL_DIR") + "/hugging-face/model/" + model_name


def get_chat_prompt(chat_arg):
    content = next((item['content'] for item in chat_arg if item['role'] == 'user'), None)
    return content.splitlines()[0].replace('User Prompt: ', '')


score_model = SentenceTransformer(get_model_path("all-MiniLM-L6-v2"))


def get_similarity_score(prediction_arg, ground_truth_arg):
    prediction_embedding = score_model.encode(prediction_arg, convert_to_tensor=True)
    ground_truth_embedding = score_model.encode(ground_truth_arg, convert_to_tensor=True)
    return util.cos_sim(prediction_embedding, ground_truth_embedding).item()

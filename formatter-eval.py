import torch
import yaml
import evaluate
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

MODEL_DIR = os.environ.get("AI_MODEL_DIR") + "/hugging-face/model/"
EVAL_MODEL = "formatter-270m"
# EVAL_MODEL = MODEL_DIR + "gemma-3-270m-it"
SCORE_MODEL = MODEL_DIR + "all-MiniLM-L6-v2"

DATA_FILE = "data/formatter-eval.yml"
ROUGE = evaluate.load("rouge")
BERT = evaluate.load("bertscore")


def get_similarity_score(prediction_arg, ground_truth_arg):
    prediction_embedding = score_model.encode(prediction_arg, convert_to_tensor=True)
    ground_truth_embedding = score_model.encode(ground_truth_arg, convert_to_tensor=True)
    return util.cos_sim(prediction_embedding, ground_truth_embedding).item()


with open(DATA_FILE, 'r', encoding='UTF-8') as file:
    dataset = yaml.safe_load(file)

device = "cuda" if torch.cuda.is_available() else "cpu"
score_model = SentenceTransformer(SCORE_MODEL)

eval_tokenizer = AutoTokenizer.from_pretrained(EVAL_MODEL)
eval_tokenizer.pad_token = eval_tokenizer.eos_token
eval_model = AutoModelForCausalLM.from_pretrained(EVAL_MODEL, dtype=torch.bfloat16, device_map=device)
eval_model.eval()

config = {
    'max_new_tokens': 500,
    'do_sample': False,
    'pad_token_id': eval_tokenizer.eos_token_id,
}

for datapoint in dataset:
    chat = datapoint['chat']
    content = next((item['content'] for item in chat if item['role'] == 'user'), None)
    prompt = content.splitlines()[0].replace('User Prompt: ', '')
    ground_truth = datapoint['ground_truth']

    input_text = eval_tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = eval_tokenizer(input_text, return_tensors="pt", truncation=True, max_length=4000)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = eval_model.generate(**inputs, **config)
    input_length = inputs["input_ids"].shape[1]
    prediction = eval_tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    similarity_score = get_similarity_score(prediction, ground_truth)
    print(prompt)
    print(similarity_score)
    print(prediction)
    print()

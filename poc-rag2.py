import argparse
import os
import time

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer,
)

parser = argparse.ArgumentParser()
parser.add_argument("--context")
parser.add_argument("question")
args = parser.parse_args()

model_dir = os.environ.get("AI_MODEL_DIR")
base_model = model_dir + "/hugging-face/model/gemma-3-4b-it"

tokenizer = AutoTokenizer.from_pretrained(base_model)

start_time = time.time()
model = AutoModelForCausalLM.from_pretrained(base_model, device_map="cuda:0", dtype=torch.bfloat16)
print(f"Model load: {time.time() - start_time}")
print(f"model parameters: {model.num_parameters():,}")

if args.context:
    with open(args.context, "r") as file:
        context = file.read()

    prompt = f"""
<start_of_turn>user
You are an expert Q&A assistant. Your answer must be based only on the provided context. If the context does not \
contain the answer, state that you 'cannot answer based on the provided documents'.

Context:
---
{context}
---

Question: {args.question}
<end_of_turn>
<start_of_turn>model
"""
else:
    prompt = args.question

for i in range(1):
    print("-" * 60)
    print(args.question)
    print()

    start_time = time.time()
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)
    print(f'text: {text}')
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    generated_ids = model.generate(
        **model_inputs,
        # max_new_tokens=32_768,
        max_new_tokens=131_072,
        streamer=streamer
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    # parsing thinking content
    try:
        # rindex finding 151_668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151_668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip(" ")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip(" ")

    # print("thinking content:", thinking_content)
    # print("content:", content)
    print(f"Text generation time: {time.time() - start_time}")

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
import torch
import bitsandbytes
#import accelerate
import time
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--context")
parser.add_argument("question")
args = parser.parse_args()

base_model = "/home/irotaru/data/hugging-face/model/gemma-3-4b-it"

tokenizer = AutoTokenizer.from_pretrained(base_model)
#print(tokenizer)

start_time = time.time()
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="cuda:0",
    dtype=torch.bfloat16,
)
print(f"Model load: {time.time() - start_time}")
#print(model)
print(f"model parameters: {model.num_parameters():,}")

if args.context:
    with open(args.context, "r") as file:
        context = file.read()

    prompt = f"""
SYSTEM: You are a contextual query answering assistant. Your answer must be based only on the provided context. If a relation is missing from context do not try to infer it. Please generate elaborated, complete and nicely crafted responses, always using markdown; if response is a list always create markdown table. If the context does not contain the answer, state that you 'cannot answer based on the provided documents'.

CONTEXT:
---
{context}
---

QUESTION: {args.question}
"""
else:
    prompt = args.question

for i in range(1):
    print("-------------------------------------------------------");
    print(args.question)
    print()

    start_time = time.time()
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True
    )
    print(f'\n\n\n------\ntext: {text}\n\n------\n\n\n')
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    print(f'model inputs length: {len(model_inputs.input_ids[0])}')

    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    generated_ids = model.generate(
        **model_inputs,
        #max_new_tokens=32_768,
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

    #print("thinking content:", thinking_content)
    #print("content:", content)
    print(f"Text generation time: {time.time() - start_time}")
    

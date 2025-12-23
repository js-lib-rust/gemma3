import argparse
import os
import time

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer, BitsAndBytesConfig,
)

parser = argparse.ArgumentParser()
parser.add_argument("--file")
parser.add_argument("--text")
args = parser.parse_args()

model_dir = os.environ.get("AI_MODEL_DIR")
base_model = model_dir + "/hugging-face/model/gemma-3-12b-it"

tokenizer = AutoTokenizer.from_pretrained(base_model)

quantization = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="cuda:0",
    dtype=torch.bfloat16,
    quantization_config=quantization)

if args.file:
    with open(args.file, "r") as file:
        text = file.read()
else:
    text = args.text
if not text:
    text = "The DHT Sensor in the kitchen reports a humidity of 13.40% and a temperature of 17.40 °C. The Thermostat \
    Sensor in the living room reports a temperature of 21.00 °C."

prompt = f"""<start_of_turn>user
Translate the following English text to Romanian. Ensure the translation is the best fit for the context and \
strictly return ONLY the translated text, preserving all original formatting (e.g., line breaks, lists, bolding, \
special characters).

{text}

<end_of_turn>
<start_of_turn>model
"""

for i in range(1):
    print("-" * 60)

    start_time = time.time()
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)
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

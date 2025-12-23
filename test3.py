from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer,
)
import torch

base_model = "D:/ai/hugging-face/model/gemma-3-4b-it"

tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="cuda:0",
    dtype=torch.bfloat16,
)

prompt = "regarding word embedding as used in llm. as far as i understand, embedding is about modeling reality in a vectorial space. given an object, we identify relevant properties, name them features, and create a vector on which every feature is represented by normalized numeric values. back to words, embedding should encapsulates word properties -- probably related to lexical analysis. now, on llm i see pretty large embedding vectors. much larger than imaginable words' properties. to understand that semantic word vector, while traversing transformers blocks, captures also features about real world represented by certain word. maybe encoding goes further than just lexical, syntactic and semantic, maybe develop a minimal understanding of reality? i asking this because i see opinions, e.g. yann lecun, that llm is not able to understand  reality"
prompt = "Couple interesting facts about Danube river."
messages = [{"role": "user", "content": prompt}]

for i in range(1):
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768,
        streamer=streamer,
    )

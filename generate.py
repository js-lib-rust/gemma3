import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--model-name", type=str, action="store", default="domain-270m")
parser.add_argument("--use-base-model", action="store_true")
parser.add_argument("--use-bfloat16", action="store_true")
parser.add_argument("--max-new-tokens", type=int, action="store", default="64")
parser.add_argument("--do-sample", action="store_true")
parser.add_argument("--samples-count", type=int, action="store", default="1")
parser.add_argument("prompt", nargs="*", default=[])
args = parser.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_dir = os.environ.get("AI_MODEL_DIR")
model_path = f"{model_dir}/hugging-face/model/{args.model_name}" if args.use_base_model else args.model_name
dtype = torch.bfloat16 if args.use_bfloat16 else torch.float32
prompt = " ".join(args.prompt)

print(f"Use device {device}")
print(f"Use model path {model_path}")
print(f"Use dtype {dtype}")
print(f"Use max new tokens {args.max_new_tokens}")
print(f"Use do sample {args.do_sample}")
print(f"Use samples count {args.samples_count}")
print()

tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token
print(f"Tokenizer loaded on {device}")

model = AutoModelForCausalLM.from_pretrained(model_path, dtype=dtype)
model.to(device)
model.eval()
print(f"Model loaded on {device}")

inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4000)
inputs = {k: v.to(device) for k, v in inputs.items()}

print("Generating response...")
print()
streamer = TextStreamer(tokenizer)
config = {
    'max_new_tokens': args.max_new_tokens,
    'do_sample': args.do_sample,
    'pad_token_id': tokenizer.eos_token_id,
    'streamer': streamer
}
for _ in range(args.samples_count):
    with torch.no_grad():
        model.generate(**inputs, **config)
        print()

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import argparse
import util

parser = argparse.ArgumentParser()
parser.add_argument("--model", action="store")
parser.add_argument("--dtype", action="store", type=util.dtype, default="float32")
parser.add_argument("--max-length", action="store", type=int, default="4000")
parser.add_argument("--max-new-tokens", action="store", type=int, default="400")
parser.add_argument("--do-sample", action="store_true")
parser.add_argument("--num-beams", action="store", type=int, default="1")
parser.add_argument("--template", action="store")
parser.add_argument("--verbose", action="store_true")
parser.add_argument("prompt", nargs="*", default=[])
args = parser.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = util.get_model_path(args.model) if args.model.startswith('/') else args.model
prompt = " ".join(args.prompt)

if args.verbose:
    print(f"Use device {device}")
    print(f"Use model path {model_path}")
    print(f"Use dtype {args.dtype}")
    print(f"Use max length {args.max_length}")
    print(f"Use max new tokens {args.max_new_tokens}")
    print(f"Use do sample {args.do_sample}")
    print(f"Use num beams {args.num_beams}")
    print(f"Use template {args.template}")
    print()

tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token
if args.verbose:
    print(f"Tokenizer loaded on {device}")

model = AutoModelForCausalLM.from_pretrained(model_path, dtype=args.dtype)
model.to(device)
model.eval()

if args.verbose:
    print(f"Model loaded on {device}")
    print("Generating response...")
    print()
streamer = TextStreamer(tokenizer)
config = {
    'max_new_tokens': args.max_new_tokens,
    'do_sample': args.do_sample,
    'num_beams': args.num_beams,
    'pad_token_id': tokenizer.eos_token_id,
    'streamer': streamer
}


def generate(prompt_arg):
    if args.template:
        prompt_arg = util.template(args.template, {'prompt': prompt_arg})
    inputs = tokenizer(prompt_arg, return_tensors="pt", truncation=True, max_length=args.max_length)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        model.generate(**inputs, **config)


if prompt:
    generate(prompt)

else:
    print(f"Generation REPL on model {model_path}")
    print()

    while True:
        line = input("- ")
        if line.lower() == "exit":
            print("Exiting...")
            break
        generate(line)
        print()

print()

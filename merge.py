from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import argparse
import util

parser = argparse.ArgumentParser()
parser.add_argument("--device", action="store", type=str, default="cpu")
parser.add_argument("--base-model", action="store", type=str)
parser.add_argument("--peft-model", action="store", type=str)
parser.add_argument("-dtype", action="store", type=util.dtype, default="float32")
parser.add_argument("--output-dir", action="store", type=str)
args = parser.parse_args()

print()
print(f"Use device {args.device}")
print(f"Use base model {args.base_model}")
print(f"Use PEFT model {args.peft_model}")
print(f"Use dtype {args.dtype}")
print(f"Use output dir {args.output_dir}")

print("Loading base model ...")
base_model_path = util.get_model_path(args.base_model) if args.base_model.startswith('/') else args.base_model
base_model = AutoModelForCausalLM.from_pretrained(base_model_path, torch_dtype=args.dtype, device_map=args.device)

print("Loading PEFT model adapters ...")
model = PeftModel.from_pretrained(base_model, args.peft_model)

print("Merging weights... this may take a minute.")
# This permanently integrates the LoRA weights into the base layers
model = model.merge_and_unload()

print(f"Saving merged model to {args.output_dir} ...")
model.save_pretrained(args.output_dir)

print(f"Saving base model tokenizer to {args.output_dir} ...")
tokenizer = AutoTokenizer.from_pretrained(args.base_model)
tokenizer.save_pretrained(args.output_dir)

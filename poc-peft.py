import torch
from peft import LoraConfig, get_peft_model
from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer
import util

model = "/gemma-3-4b-it"
model_path = util.get_model_path(model) if model.startswith('/') else model
device = "cuda:0" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map=device,
    dtype=dtype,
)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

tokenizer = AutoTokenizer.from_pretrained(model_path)
terminators = [tokenizer.eos_token_id]

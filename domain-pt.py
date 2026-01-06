import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, \
    DataCollatorForLanguageModeling
from datasets import Dataset
import argparse
import os
import util


def prepare_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]  # Remove leading/trailing whitespace
    return lines


def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=args.max_length)


# ---------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--use-tuned-model", action="store_true")
parser.add_argument("--files", type=util.split_by_comma, action="store")
parser.add_argument("--output-dir", type=str, action="store", default="domain-270m")
parser.add_argument("--max-length", type=int, action="store", default="500")
parser.add_argument("--epochs", type=int, action="store", default="2")
parser.add_argument("--train-batch", type=int, action="store", default="2")
parser.add_argument("--learning-rate", type=float, action="store", default="5e-6")
parser.add_argument("--weight-decay", type=float, action="store", default="0.01")
parser.add_argument("--wakeup", type=float, action="store", default="0.05")
parser.add_argument("--use-mixed-precision", action="store_true")
parser.add_argument("prompt", nargs="*", default=[])
args = parser.parse_args()

print(args.prompt)

MODEL_DIR = os.environ.get("AI_MODEL_DIR")
MODEL_NAME = MODEL_DIR + "/hugging-face/model/gemma-3-270m-it"
DATA_FILE = "data/medical.md"
DTYPE = torch.float32
print()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = f"./{args.output_dir}"
model_path = output_dir if args.use_tuned_model else MODEL_NAME
print(f"Use device {device}")
print(f"Use model {model_path}")
print(f"Use output dir {output_dir}")
print(f"Use max length {args.max_length}")
print(f"Use epochs {args.epochs}")
print(f"Use train batch size {args.train_batch}")
print(f"Use learning rate {args.learning_rate}")
print(f"Use weight decay {args.weight_decay}")
print(f"Use wakeup ratio {args.wakeup}")
print(f"Use mixed precision {args.use_mixed_precision}")
print()

domain_data = prepare_dataset(DATA_FILE)
dataset = Dataset.from_dict({"text": domain_data})

tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token
tokenized_datasets = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
print(tokenized_datasets)

model = AutoModelForCausalLM.from_pretrained(model_path)
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=args.epochs,
    per_device_train_batch_size=args.train_batch,
    gradient_accumulation_steps=1,
    learning_rate=args.learning_rate,
    weight_decay=args.weight_decay,
    logging_dir="./logs",
    logging_steps=10,
    save_strategy="epoch",
    fp16=args.use_mixed_precision,
    bf16=False,
    optim="adamw_torch",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    data_collator=data_collator,
    processing_class=tokenizer,
)
trainer.train()

trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"Domain pre-training complete! Model saved to {output_dir}")

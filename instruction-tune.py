import json

import torch
import yaml
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import os
import argparse
import util


def tokenizer_function(examples):
    tokenized = tokenizer(
        examples['text'],
        max_length=args.max_length,
        truncation=True,
        padding="max_length",
        return_tensors=None,
    )
    return tokenized


def prepare_dataset(examples):
    processed_examples = []
    for example in examples:
        if not tools_support and tools:
            util.inject_tools(tools, example, True)
        if args.trace:
            print(f"example: {example}")
            print()

        tools_arg = tools if tools_support else None
        text = tokenizer.apply_chat_template(example, tools=tools_arg, tokenize=False)

        if args.trace:
            print(f"text: {text}")
            print()
        processed_examples.append({"text": text})
    return processed_examples


# ---------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--model", action="store", type=str)
parser.add_argument("--use-peft-lora", action="store_true")
parser.add_argument("--dtype", action="store", type=util.dtype, default="float32")
parser.add_argument("--files", action="store", type=util.split_by_comma)
parser.add_argument("--tools", action="store", type=util.split_by_comma)
parser.add_argument("--output-dir", action="store", type=str)
parser.add_argument("--max-length", action="store", type=int, default="1000")
parser.add_argument("--epochs", action="store", type=int, default="4")
parser.add_argument("--train-batch", action="store", type=int, default="2")
parser.add_argument("--learning-rate", action="store", type=float, default="5e-6")
parser.add_argument("--weight-decay", action="store", type=float, default="0.01")
parser.add_argument("--wakeup", action="store", type=float, default="0.05")
parser.add_argument("--use-mixed-precision", action="store_true")
parser.add_argument("--use-resize-embeddings", action="store_true")
parser.add_argument("--trace", action="store_true")
args = parser.parse_args()

print()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = f"./{args.output_dir}"
model_path = util.get_model_path(args.model) if args.model.startswith('/') else args.model
dtype = args.dtype
if args.use_peft_lora:
    dtype = torch.bfloat16
print(f"Use device {device}")
print(f"Use model {model_path}")
print(f"Use PEFT LORA {args.use_peft_lora}")
print(f"Use dtype {dtype}")
print(f"Use files {args.files}")
print(f"Use tools {args.tools}")
print(f"Use output dir {output_dir}")
print(f"Use max length {args.max_length}")
print(f"Use epochs {args.epochs}")
print(f"Use train batch size {args.train_batch}")
print(f"Use learning rate {args.learning_rate}")
print(f"Use weight decay {args.weight_decay}")
print(f"Use wakeup ratio {args.wakeup}")
print(f"Use mixed precision {args.use_mixed_precision}")
print(f"Use resize embeddings {args.use_resize_embeddings}")
print(f"Use trace {args.trace}")
print()

if args.tools:
    tools = []
    for file_name in args.tools:
        with open(f"data/{file_name}", 'r', encoding='UTF-8') as file:
            tools += json.load(file)
    if args.trace:
        print(f"tools: {tools}")
        print()
else:
    tools = None

print(f"Loading model {model_path}...")
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=dtype, device_map=device, attn_implementation="eager")
print(f"Model loaded on {device}")
print(f"Model parameters: {model.num_parameters():,}")

if args.use_peft_lora:
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    # if args.use_tuned_model and os.path.exists(f"{output_dir}/adapter_model.safetensors"):
    #     print("Loading previous PEFT adapters...")
    #     model.load_adapter("function-1b", output_dir)
    model.print_trainable_parameters()

print(f"Loading tokenizer from: {model_path}")
tokenizer = AutoTokenizer.from_pretrained(model_path)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
tokenizer.truncation_side = "right"
tools_support = util.has_tools_support(tokenizer)
print(f"Model tools {'not ' if not tools_support else ''}supported")

model.config.pad_token_id = tokenizer.pad_token_id
model.config.bos_token_id = tokenizer.bos_token_id
model.config.eos_token_id = tokenizer.eos_token_id
if hasattr(model, 'generation_config'):
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.bos_token_id = tokenizer.bos_token_id
if args.use_resize_embeddings:
    model.resize_token_embeddings(len(tokenizer))

print()
data_examples = []
for data_file in args.files:
    data_file = f"data/{data_file}"
    with open(data_file, 'r', encoding='UTF-8') as file_name:
        file_examples = yaml.safe_load(file_name)
        print(f"Loaded {len(file_examples)} tests from the file `{os.path.abspath(data_file)}`.")
        data_examples += file_examples

print("Preparing dataset...")
processed_data = prepare_dataset(data_examples)
print(f"Processed {len(processed_data)} examples")

dataset = Dataset.from_list(processed_data)
if len(dataset) > 20:
    dataset_split = dataset.train_test_split(test_size=0.1, seed=42, shuffle=True)
    train_dataset = dataset_split["train"]
    validation_dataset = dataset_split["test"]
else:
    train_dataset = dataset
    validation_dataset = dataset
print(f"Dataset split:")
print(f"- Training examples: {len(train_dataset)}")
print(f"- Validation examples: {len(validation_dataset)}")

print("Tokenizing datasets...")
train_tokens = train_dataset.map(tokenizer_function, batched=True)
train_tokens = train_tokens.map(lambda examples: {"labels": examples["input_ids"].copy()}, batched=True)
validation_tokens = validation_dataset.map(tokenizer_function, batched=True)
validation_tokens = validation_tokens.map(lambda examples: {"labels": examples["input_ids"].copy()}, batched=True)
print(f"Tokenized train size: {len(train_tokens)}")
print(f"Tokenized validation size: {len(validation_tokens)}")

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=args.epochs,
    per_device_train_batch_size=args.train_batch,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=1,
    warmup_ratio=args.wakeup,
    learning_rate=args.learning_rate,
    lr_scheduler_type="cosine",
    weight_decay=args.weight_decay,
    logging_steps=5,
    save_steps=20,
    eval_steps=10,
    eval_strategy="steps",
    fp16=args.use_mixed_precision,
    gradient_checkpointing=False,
    optim="adamw_torch",
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    report_to="none",
    push_to_hub=False,
    dataloader_pin_memory=False,
    remove_unused_columns=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_tokens,
    eval_dataset=validation_tokens,
    data_collator=data_collator,
    processing_class=tokenizer,
)

print()
print("Starting training...")
train_result = trainer.train()

print()
print(f"Saving model to {output_dir}")
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)
model.config.save_pretrained(output_dir)

print(f"Training completed!")

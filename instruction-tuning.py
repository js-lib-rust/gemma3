import json

import torch
import yaml
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
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
    if args.assert_max_length:
        tokenized = tokenizer(examples['text'], truncation=False, padding=False, return_tensors=None)
        for tokens in tokenized['input_ids']:
            assert len(tokens) < args.max_length, f"max length exceeded: {len(tokens) + 1}"

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
        tools = tools_map.get(example['agent_name'], None)
        example = example['example']
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
parser.add_argument("--device", action="store", type=str, default="cuda:0")
parser.add_argument("--model", action="store", type=str)
parser.add_argument("--peft", action="store", type=str, choices=["LoRA", "QLoRA"])
parser.add_argument("--lora-targets", action="store", type=str,
                    choices=["attention", "attention+MLP", "attention+MLP+embedding"], default="attention+MLP")
parser.add_argument("--lora-save-embeddings", action="store_true")
parser.add_argument("--peft-merge", action="store_true")
parser.add_argument("--dtype", action="store", type=util.dtype, default="float32")
parser.add_argument("--attention", action="store", type=str,
                    choices=["eager", "flash_attention_2", "sdpa"], default="eager")
parser.add_argument("--files", action="store", type=util.split_by_comma)
parser.add_argument("--tools", action="store", type=util.split_by_comma)
parser.add_argument("--output-dir", action="store", type=str)
parser.add_argument("--max-length", action="store", type=int, default="1000")
parser.add_argument("--assert-max-length", action="store_true")
parser.add_argument("--epochs", action="store", type=int, default="4")
parser.add_argument("--train-batch", action="store", type=int, default="2")
parser.add_argument("--learning-rate", action="store", type=float, default="5e-6")
parser.add_argument("--weight-decay", action="store", type=float, default="0.01")
parser.add_argument("--wakeup", action="store", type=float, default="0.05")
parser.add_argument("--fp16", action="store_true")
parser.add_argument("--bf16", action="store_true")
parser.add_argument("--resize-embeddings", action="store_true")
parser.add_argument("--logging-steps", action="store", type=int, default="5")
parser.add_argument("--eval-steps", action="store", type=int, default="10")
parser.add_argument("--save-steps", action="store", type=int, default="20")
parser.add_argument("--trace", action="store_true")
args = parser.parse_args()

print()

device = args.device if torch.cuda.is_available() else "cpu"
output_dir = f"./{args.output_dir}"
model_path = util.get_model_path(args.model) if args.model.startswith('/') else args.model
dtype = args.dtype
if args.peft:
    dtype = torch.bfloat16
print(f"Use device {device}")
print(f"Use model {model_path}")
print(f"Use PEFT {args.peft}")
print(f"Use LoRA target modules {args.lora_targets}")
print(f"Use LoRA save embedding modules {args.lora_save_embeddings}")
print(f"Use PEFT merge {args.peft_merge}")
print(f"Use dtype {dtype}")
print(f"Use attention implementation {args.attention}")
print(f"Use files {args.files}")
print(f"Use tools {args.tools}")
print(f"Use output dir {output_dir}")
print(f"Use max length {args.max_length}")
print(f"Use assert max length {args.assert_max_length}")
print(f"Use epochs {args.epochs}")
print(f"Use train batch size {args.train_batch}")
print(f"Use learning rate {args.learning_rate}")
print(f"Use weight decay {args.weight_decay}")
print(f"Use wakeup ratio {args.wakeup}")
print(f"Use fp16 {args.fp16}")
print(f"Use bf16 {args.bf16}")
print(f"Use resize embeddings {args.resize_embeddings}")
print(f"Use logging steps {args.logging_steps}")
print(f"Use evaluation steps {args.eval_steps}")
print(f"Use save steps {args.save_steps}")
print(f"Use trace {args.trace}")
print()

tools_map = {}
if args.tools:
    for file_name in args.tools:
        tools_file = f"data/{file_name}"
        agent_name = os.path.basename(tools_file).split('.', 1)[0]
        with open(tools_file, 'r', encoding='UTF-8') as file:
            tools_map[agent_name] = json.load(file)
    if args.trace:
        print(f"tools_map: {tools_map}")
        print()

print(f"Loading model {model_path}...")
model_config = {
    'dtype': dtype,
    'device_map': device,
    'attn_implementation': args.attention
}
if args.peft == "QLoRA":
    print("Adding QLoRA parameters to model configuration")
    model_config['load_in_4bit'] = True
    model_config['bnb_4bit_compute_dtype'] = dtype
model = AutoModelForCausalLM.from_pretrained(model_path, **model_config)
if args.peft == "QLoRA":
    print("Preparing model for QLoRA training")
    model = prepare_model_for_kbit_training(model)

print(f"Model loaded on {device}")
print(f"Model parameters: {model.num_parameters():,}")
if args.peft:
    ensure_weight_tying = False
    target_modules = []
    modules_to_save = None

    if "embedding" in args.lora_targets:
        model.config.tie_word_embeddings = False
        target_modules.append("embed_tokens")
        target_modules.append("lm_head")
    if "attention" in args.lora_targets:
        target_modules.append("q_proj")
        target_modules.append("k_proj")
        target_modules.append("v_proj")
        target_modules.append("o_proj")
    if "MLP" in args.lora_targets:
        target_modules.append("gate_proj")
        target_modules.append("up_proj")
        target_modules.append("down_proj")

    if args.lora_save_embeddings:
        modules_to_save = ["embed_tokens", "lm_heads"]
        ensure_weight_tying = True

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=target_modules,
        modules_to_save=modules_to_save,
        ensure_weight_tying=ensure_weight_tying,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    print(f"LoRA config: {lora_config}")
    print("Adapting model for PEFT")
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

print(f"Loading tokenizer from {model_path}")
tokenizer = AutoTokenizer.from_pretrained(model_path)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
tokenizer.truncation_side = "right"
tools_support = util.has_tools_support(tokenizer)
print(f"Model tools {'not ' if not tools_support else ''}supported")
if args.tools:
    print("Monkey patch on tokenizer.apply_chat_template for tool argument order.")
    util.patch_tokenizer(tokenizer)

model.config.pad_token_id = tokenizer.pad_token_id
model.config.bos_token_id = tokenizer.bos_token_id
model.config.eos_token_id = tokenizer.eos_token_id
if hasattr(model, 'generation_config'):
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.bos_token_id = tokenizer.bos_token_id
if args.resize_embeddings:
    model.resize_token_embeddings(len(tokenizer))

print()
data_examples = []
for data_file in args.files:
    data_file = f"data/{data_file}"
    agent_name = os.path.basename(data_file).split('.', 1)[0]
    with open(data_file, 'r', encoding='UTF-8') as file_name:
        # yaml knows to load json
        file_examples = yaml.safe_load(file_name)
        print(f"Loaded {len(file_examples)} tests from the file `{os.path.abspath(data_file)}`.")
        data_examples += [{'agent_name': agent_name, 'example': example} for example in file_examples]

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
# train_tokens = train_tokens.map(lambda examples: {"labels": examples["input_ids"].copy()}, batched=True)
validation_tokens = validation_dataset.map(tokenizer_function, batched=True)
# validation_tokens = validation_tokens.map(lambda examples: {"labels": examples["input_ids"].copy()}, batched=True)
print(f"Tokenized train size: {len(train_tokens)}")
print(f"Tokenized validation size: {len(validation_tokens)}")

training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=args.epochs,
    per_device_train_batch_size=args.train_batch,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=1,
    warmup_ratio=args.wakeup,
    optim="adamw_torch",
    learning_rate=args.learning_rate,
    lr_scheduler_type="cosine",
    weight_decay=args.weight_decay,
    metric_for_best_model="eval_loss",
    eval_strategy="steps",
    logging_steps=args.logging_steps,
    eval_steps=args.eval_steps,
    save_steps=args.save_steps,
    fp16=args.fp16,
    bf16=args.bf16,
    gradient_checkpointing=False,
    save_total_limit=2,
    load_best_model_at_end=True,
    greater_is_better=False,
    report_to="none",
    push_to_hub=False,
    dataloader_pin_memory=False,
    remove_unused_columns=True,
)
print(f"Training arguments: {training_args}")

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
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
if args.peft_merge:
    print("Merging PEFT weights into base model")
    model = model.merge_and_unload()

model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

print(f"Training completed!")

import torch
import yaml
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
        if 'chat' in example:
            text = tokenizer.apply_chat_template(example['chat'], tokenize=False)
            processed_examples.append({"text": text})
        else:
            print(f"Warning: Example missing 'messages' key: {example.keys()}")
    return processed_examples


# ---------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--use-tuned-model", action="store_true")
parser.add_argument("--model", action="store")
parser.add_argument("--files", type=util.split_by_comma, action="store")
parser.add_argument("--output-dir", type=str, action="store", default="formatter-270m")
parser.add_argument("--max-length", type=int, action="store", default="800")
parser.add_argument("--epochs", type=int, action="store", default="4")
parser.add_argument("--train-batch", type=int, action="store", default="2")
parser.add_argument("--learning-rate", type=float, action="store", default="5e-6")
parser.add_argument("--weight-decay", type=float, action="store", default="0.01")
parser.add_argument("--wakeup", type=float, action="store", default="0.05")
parser.add_argument("--use-mixed-precision", action="store_true")
args = parser.parse_args()

MODEL_DIR = os.environ.get("AI_MODEL_DIR")
MODEL_NAME = MODEL_DIR + "/hugging-face/model/gemma-3-270m-it"
DATA_SET = ["medical-response-set", "hera-response-set", "weather-response-set"]
DTYPE = torch.float32
print()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = f"./{args.output_dir}"
data_files = args.files if args.files else DATA_SET
model_name = args.model if args.model else MODEL_NAME
model_path = output_dir if args.use_tuned_model else model_name
print(f"Use device {device}")
print(f"Use model {model_path}")
print(f"Use data files {data_files}")
print(f"Use output dir {output_dir}")
print(f"Use max length {args.max_length}")
print(f"Use epochs {args.epochs}")
print(f"Use train batch size {args.train_batch}")
print(f"Use learning rate {args.learning_rate}")
print(f"Use wakeup ratio {args.wakeup}")
print(f"Use mixed precision {args.use_mixed_precision}")
print()

print(f"Loading model {model_path}...")
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=DTYPE, device_map=device, attn_implementation="eager")
print(f"Model loaded on {device}")
print(f"Model parameters: {model.num_parameters():,}")

print(f"Loading tokenizer from: {model_path}")
tokenizer = AutoTokenizer.from_pretrained(model_path)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
tokenizer.truncation_side = "right"

model.config.pad_token_id = tokenizer.pad_token_id
model.config.bos_token_id = tokenizer.bos_token_id
model.config.eos_token_id = tokenizer.eos_token_id
if hasattr(model, 'generation_config'):
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.bos_token_id = tokenizer.bos_token_id
model.resize_token_embeddings(len(tokenizer))

data_examples = []
for data_file in data_files:
    data_file = f"data/{data_file}.yml"
    with open(data_file, 'r', encoding='UTF-8') as file:
        file_examples = yaml.safe_load(file)
        print(f"Loaded {len(file_examples)} tests from the file `{os.path.abspath(data_file)}`.")
        data_examples += file_examples

print("Preparing dataset...")
processed_data = prepare_dataset(data_examples)
print(f"Processed {len(processed_data)} examples")

dataset = Dataset.from_list(processed_data)
if len(dataset) > 20:
    dataset_split = dataset.train_test_split(test_size=0.1, seed=42)
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

print(f"Training completed!")

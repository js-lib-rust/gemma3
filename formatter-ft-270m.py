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

MODEL_DIR = os.environ.get("AI_MODEL_DIR")
MODEL_NAME = MODEL_DIR + "/hugging-face/model/gemma-3-270m-it"
# MODEL_NAME = "./formatter-270m"
OUTPUT_DIR = "./formatter-270m"
YAML_FILE = "formatter-set-270m.yml"

DTYPE = torch.float32
MAX_LENGTH = 1024
print()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"device: {device}")

print(f"Loading model {MODEL_NAME}...")
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=DTYPE, device_map=device)
print(f"Model loaded on {device}")
print(f"Model parameters: {model.num_parameters():,}")

print(f"Loading tokenizer from: {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
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


def load_yaml_data(file_path):
    """Load training data from YAML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['examples'] if 'examples' in data else data


print(f"Loading training data from: {YAML_FILE}")
yaml_data = load_yaml_data(YAML_FILE)
print(f"Loaded {len(yaml_data)} examples")


def prepare_dataset(examples):
    """Convert YAML examples to training format using chat template"""
    processed_examples = []
    for example in examples:
        if 'messages' in example:
            text = tokenizer.apply_chat_template(example['messages'], tokenize=False)
            processed_examples.append({"text": text})
        else:
            print(f"Warning: Example missing 'messages' key: {example.keys()}")
    return processed_examples


print("Preparing dataset...")
processed_data = prepare_dataset(yaml_data)
print(f"Processed {len(processed_data)} examples")

dataset = Dataset.from_list(processed_data)
train_test_split = dataset.train_test_split(test_size=0.12, seed=42)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

print(f"Dataset split:")
print(f"  Training examples: {len(train_dataset)}")
print(f"  Validation examples: {len(eval_dataset)}")


def tokenizer_function(examples):
    tokenized = tokenizer(
        examples['text'],
        max_length=MAX_LENGTH,
        truncation=True,
        padding="max_length",
        return_tensors=None,
    )
    return tokenized


print("Tokenizing datasets...")
tokenized_train = train_dataset.map(tokenizer_function, batched=True)
tokenized_eval = eval_dataset.map(tokenizer_function, batched=True)

tokenized_train = tokenized_train.map(
    lambda examples: {"labels": examples["input_ids"].copy()},
    batched=True
)
tokenized_eval = tokenized_eval.map(
    lambda examples: {"labels": examples["input_ids"].copy()},
    batched=True
)

print(f"tokenized_train: {tokenized_train}")
# print(f"input_ids: {tokenized_train['input_ids']}")
# print(f"attention_mask: {tokenized_train['attention_mask']}")
# print(f"labels: {tokenized_train['labels']}")
print(f"Tokenized train size: {len(tokenized_train)}")
print(f"Tokenized eval size: {len(tokenized_eval)}")

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=1,
    warmup_ratio=0.05,
    learning_rate=2e-5,
    lr_scheduler_type="cosine",
    logging_steps=5,
    save_steps=20,
    eval_steps=10,
    eval_strategy="steps",
    fp16=torch.cuda.is_available(),
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
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    data_collator=data_collator,
    processing_class=tokenizer,
)

print()
print("Starting training...")
train_result = trainer.train()

print()
print(f"Saving model to {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"Training completed!")


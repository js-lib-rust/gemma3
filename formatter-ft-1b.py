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
from peft import LoraConfig, get_peft_model
import os

MODEL_DIR = os.environ.get("AI_MODEL_DIR")
MODEL_NAME = MODEL_DIR + "/hugging-face/model/gemma-3-1b-it"
OUTPUT_DIR = "./formatter-1b"
YAML_FILE = "data/formatter-set.yml"

DTYPE = torch.bfloat16
MAX_LENGTH = 1024
print()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"device: {device}")

print(f"Loading model {MODEL_NAME}...")
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=DTYPE, device_map=device)
print(f"Model loaded on {device}")
print(f"Model parameters: {model.num_parameters():,}")

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

print(f"Loading tokenizer from {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.pad_token_id
model.config.eos_token_id = tokenizer.eos_token_id


# Load YAML data
def load_yaml_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['examples'] if 'examples' in data else data


print(f"\nLoading training data from: {YAML_FILE}")
yaml_data = load_yaml_data(YAML_FILE)
print(f"Loaded {len(yaml_data)} examples")


# Prepare dataset using apply_chat_template
def prepare_dataset(examples):
    """Convert YAML examples to training format using chat template"""
    processed_examples = []

    for example in examples:
        if 'messages' in example:
            # Apply chat template to get text format
            formatted_text = tokenizer.apply_chat_template(
                example['messages'],
                tokenize=False,  # Get text, not tokens
                add_generation_prompt=False,
            )

            processed_examples.append({
                "text": formatted_text
            })
        else:
            print(f"Warning: Example missing 'messages' key: {example.keys()}")

    return processed_examples


# Prepare the dataset
print("\nPreparing dataset...")
processed_data = prepare_dataset(yaml_data)
print(f"Processed {len(processed_data)} examples")

# Create Hugging Face Dataset
dataset = Dataset.from_list(processed_data)

# Split into train and validation
train_test_split = dataset.train_test_split(test_size=0.15, seed=42)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

print(f"\nDataset split:")
print(f"  Training examples: {len(train_dataset)}")
print(f"  Validation examples: {len(eval_dataset)}")


# FIXED: Tokenization function with proper truncation and padding
def tokenize_function(examples):
    # First tokenize with truncation
    tokenized = tokenizer(
        examples["text"],
        truncation=True,
        padding=False,  # We'll pad separately
        max_length=MAX_LENGTH,
        return_tensors=None
    )

    # Then pad the sequences to same length
    padded = tokenizer.pad(
        tokenized,
        padding=True,
        max_length=MAX_LENGTH,
        return_tensors=None
    )

    # Add labels (same as input_ids for causal LM)
    padded["labels"] = padded["input_ids"].copy()

    return padded


# Apply tokenization
print("\nTokenizing datasets...")
# Using the simple version - recommended
tokenized_train = train_dataset.map(
    lambda examples: tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors=None
    ),
    batched=True
)

tokenized_eval = eval_dataset.map(
    lambda examples: tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors=None
    ),
    batched=True
)

# Add labels
tokenized_train = tokenized_train.map(
    lambda examples: {"labels": examples["input_ids"].copy()},
    batched=True
)
tokenized_eval = tokenized_eval.map(
    lambda examples: {"labels": examples["input_ids"].copy()},
    batched=True
)

print(f"Tokenized train size: {len(tokenized_train)}")
print(f"Tokenized eval size: {len(tokenized_eval)}")

# Data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=1,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=1,
    warmup_steps=10,
    logging_steps=5,
    save_steps=50,
    eval_steps=25,
    eval_strategy="steps",
    learning_rate=2e-4,
    fp16=torch.cuda.is_available(),
    gradient_checkpointing=False,
    optim="adamw_torch",
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    report_to="none",
    push_to_hub=False,
    remove_unused_columns=True,
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    data_collator=data_collator,
    processing_class=tokenizer,
)

# Train
print("\nStarting training...")
train_result = trainer.train()

# Save everything
print(f"\nSaving model to {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\nTraining completed!")
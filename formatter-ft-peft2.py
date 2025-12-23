import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model

# Configuration
MODEL_NAME = "D:/ai/hugging-face/model/gemma-3-1b-it"
OUTPUT_DIR = "./gemma-formatter-peft"

print(f"Loading tokenizer from: {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Set pad token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# FIX 1: Simple function that returns individual examples (not lists)
def create_training_examples():
    """Create training examples as individual dicts"""
    examples = [
        {
            "system_prompt": "Respond to the next user prompt using provided function response. You are free to \
augment the response but do not add your thinking explanations.",
            "user_prompt": "please list today health measurements",
            "function_response": """{"timestamp":"2025-12-17 08:47:02","person":"Iulian Rotaru","measurement":\
"systolic_pressure","value":124}
{"timestamp":"2025-12-17 08:47:02","person":"Iulian Rotaru","measurement":"diastolic_pressure","value":81}""",
            "assistant_response": "Here are your health measurements:\n*   **Systolic Pressure:** 124 mmHg\n*   \
            **Diastolic Pressure:** 81 mmHg"
        },
        {
            "system_prompt": "Respond to the next user prompt using provided function response. You are free to \
augment the response but do not add your thinking explanations.",
            "user_prompt": "what's my temperature?",
            "function_response": """{"timestamp":"2025-12-17 10:00:00","person":"Iulian Rotaru","measurement":\
"body_temperature","value":36.5}""",
            "assistant_response": "Your body temperature is 36.5 °C."
        }
    ]
    return examples


def create_validation_examples():
    """Create validation examples"""
    return [
        {
            "system_prompt": "Respond to the next user prompt using provided function response. You are free to \
augment the response but do not add your thinking explanations.",
            "user_prompt": "show my blood pressure",
            "function_response": """{"timestamp":"2025-12-17 08:30:00","person":"Iulian Rotaru","measurement":
"systolic_pressure","value":118}
{"timestamp":"2025-12-17 08:30:00","person":"Iulian Rotaru","measurement":"diastolic_pressure","value":76}""",
            "assistant_response": "Your blood pressure:\n*   **Systolic:** 118 mmHg\n*   **Diastolic:** 76 mmHg"
        }
    ]


# FIX 2: Pre-process examples into text before creating dataset
def preprocess_examples(examples):
    """Convert examples to text format"""
    processed = []
    for example in examples:
        # Create the full training text
        instruction = f"{example['system_prompt']}\n\nUser Prompt: {example['user_prompt']}\n\nFunction Response:\n\
{example['function_response']}"
        full_text = f"{instruction}\n\nAssistant Response: {example['assistant_response']}{tokenizer.eos_token}"
        processed.append(full_text)
    return processed


# Get examples and preprocess
train_examples = create_training_examples()
eval_examples = create_validation_examples()

train_texts = preprocess_examples(train_examples)
eval_texts = preprocess_examples(eval_examples)

print(f"Created {len(train_texts)} training examples")
print(f"Created {len(eval_texts)} validation examples")

# FIX 3: Create dataset with individual text entries
train_dataset = Dataset.from_dict({"text": train_texts})
eval_dataset = Dataset.from_dict({"text": eval_texts})

# Debug: Check first example
print("\nFirst training example preview:")
print(train_dataset[0]["text"][:200] + "...")


# FIX 4: Tokenization function with proper handling
def tokenize_function(examples):
    # Tokenize with padding and truncation
    tokenized = tokenizer(
        examples["text"],
        truncation=True,
        padding=True,  # ADD THIS: enables padding
        max_length=256,
        return_tensors=None  # Returns lists, not tensors
    )

    # For causal LM, labels are the same as input_ids
    tokenized["labels"] = tokenized["input_ids"].copy()

    return tokenized


# Tokenize datasets
print("\nTokenizing datasets...")
tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_eval = eval_dataset.map(tokenize_function, batched=True)

print(f"Tokenized train size: {len(tokenized_train)}")
print(f"Tokenized eval size: {len(tokenized_eval)}")

# FIX 5: Load model
print(f"\nLoading model: {MODEL_NAME}")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="cuda" if torch.cuda.is_available() else None,
)

# Ensure model config matches tokenizer
model.config.pad_token_id = tokenizer.pad_token_id
model.config.eos_token_id = tokenizer.eos_token_id
print(f"Model loaded. Parameters: {model.num_parameters():,}")

# FIX 6: Apply LoRA
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

# FIX 7: Data collator - simplified
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# FIX 8: Training arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=400,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=1,
    warmup_steps=5,
    logging_steps=5,
    save_steps=50,
    eval_steps=50,
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
    remove_unused_columns=True,  # Let trainer handle columns
)
print("after training parameters")

# FIX 9: Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    data_collator=data_collator,
    processing_class=tokenizer,
)
print("after trainer")

# Train
print("\nStarting training...")
trainer.train()

# Save
print(f"\nSaving model to {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\nTraining completed!")

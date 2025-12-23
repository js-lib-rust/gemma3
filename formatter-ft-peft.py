import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq, DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model
import os

# Configuration
MODEL_NAME = "D:/ai/hugging-face/model/gemma-3-1b-it"
OUTPUT_DIR = "./gemma-formatter-peft"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#tokenizer.padding_side = "right"
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Formatting function
def format_training_example(example):
    """Format a single training example"""
    # Create instruction
    instruction = f"{example['system_prompt']}\n\nUser Prompt: {example['user_prompt']}\n\nFunction Response:\n{example['function_response']}"

    # Format for chat template
    messages = [
        {"role": "user", "content": instruction},
        {"role": "assistant", "content": example['assistant_response']}
    ]

    # Apply chat template
    formatted = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )

    # Tokenize
    tokenized = tokenizer(formatted, truncation=True, max_length=1024)

    # Add labels for causal LM
    tokenized["labels"] = tokenized["input_ids"].copy()

    return tokenized


# Create training dataset
def create_training_dataset():
    """Create diverse training examples"""
    examples = [
        {
            "system_prompt": "Responde to the next user prompt using provided function response. You are free to augment the response but do not add your thinking explanations.",
            "user_prompt": "please list today health measurements",
            "function_response": """{"timestamp":"2025-12-17 08:47:02","person":"Iulian Rotaru","measurement":"systolic_pressure","value":124}
{"timestamp":"2025-12-17 08:47:02","person":"Iulian Rotaru","measurement":"diastolic_pressure","value":81}""",
            "assistant_response": "Here are your health measurements:\n*   **Systolic Pressure:** 124 mmHg\n*   **Diastolic Pressure:** 81 mmHg"
        },
        {
            "system_prompt": "Responde to the next user prompt using provided function response. You are free to augment the response but do not add your thinking explanations.",
            "user_prompt": "what's my temperature?",
            "function_response": """{"timestamp":"2025-12-17 10:00:00","person":"Iulian Rotaru","measurement":"body_temperature","value":36.5}""",
            "assistant_response": "Your body temperature is 36.5 °C."
        }
    ]

    # Create dataset
    dataset = Dataset.from_list(examples)

    # Apply formatting
    tokenized_dataset = dataset.map(
        format_training_example,
        remove_columns=dataset.column_names
    )

    return tokenized_dataset


# Create validation dataset
def create_validation_dataset():
    """Create validation examples"""
    examples = [
        {
            "system_prompt": "Responde to the next user prompt using provided function response. You are free to augment the response but do not add your thinking explanations.",
            "user_prompt": "show my weight",
            "function_response": """{"timestamp":"2025-12-17 09:00:00","person":"Iulian Rotaru","measurement":"body_weight","value":75.5}""",
            "assistant_response": "Your weight is 75.5 kg."
        }
    ]

    dataset = Dataset.from_list(examples)
    tokenized_dataset = dataset.map(
        format_training_example,
        remove_columns=dataset.column_names
    )

    return tokenized_dataset


# Main training function
def fine_tune_model():
    print(f"Loading model: {MODEL_NAME}")

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        attn_implementation="eager"
    )
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.eos_token_id = tokenizer.eos_token_id
    print(f"Model loaded. Parameters: {model.num_parameters():,}")

    # Configure LoRA
    lora_config = LoraConfig(
        r=8,  # Smaller rank for 1B model
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # Target attention layers
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Prepare datasets
    print("Preparing datasets...")
    train_dataset = create_training_dataset()
    eval_dataset = create_validation_dataset()

    # Data collator
    # data_collator = DataCollatorForSeq2Seq(
    #     tokenizer=tokenizer,
    #     padding=True,
    #     return_tensors="pt"
    # )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # False for causal language modeling
        #pad_to_multiple_of=8  # Better performance on GPUs
    )

    # FIXED: Use 'eval_strategy' instead of 'evaluation_strategy'
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=10,  # Start with fewer epochs
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=2,
        warmup_steps=10,
        logging_steps=3,
        save_steps=50,
        eval_steps=50,
        eval_strategy="steps",  # CHANGED from evaluation_strategy
        learning_rate=2e-4,
        fp16=torch.cuda.is_available(),
        gradient_checkpointing=False,  # Disable for simplicity
        optim="adamw_torch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        push_to_hub=False,
    )

    # Create Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    # Train
    print("Starting training...")
    train_result = trainer.train()

    # Save model
    trainer.save_model()
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"Training completed! Model saved to {OUTPUT_DIR}")

    return model, tokenizer


# Run training
if __name__ == "__main__":
    fine_tune_model()
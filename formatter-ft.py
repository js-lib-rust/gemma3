import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
# from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import yaml

# 1. Load the base model and tokenizer
# model_name = "./gemma-formatter-simple"
model_name = "D:/ai/hugging-face/model/gemma-3-1b-it"
#model_name = "./gemma-formatter-simple-fp16"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config, torch_dtype=torch.float16)
#model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Set padding token
tokenizer.pad_token = tokenizer.eos_token


# 2. Prepare your training data
def create_training_examples():
    with open('formatter-set-small.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['examples']


# Apply chat template to format examples
def apply_chat_template(example):
    # Tokenizer handles all special tokens automatically
    formatted = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=True,  # Returns token IDs
        padding="max_length",
        truncation=True,
        max_length=2000,
        return_tensors=None  # Returns list, not tensor
    )

    # For causal LM training, labels = input_ids
    return {"input_ids": formatted, "labels": formatted}


# 3. Create dataset
train_data = create_training_examples()
print(train_data)
dataset = Dataset.from_list(train_data)
print(dataset)
tokenized_dataset = dataset.map(apply_chat_template)
print(tokenized_dataset)

# 4. Tokenize the data
def tokenize_function(examples):
    return tokenizer(
        examples,
        truncation=True,
        padding=True,
        max_length=2000
    )


#tokenized_dataset = formatted_dataset.map(tokenize_function, batched=True)

# 5. Set up training
training_args = TrainingArguments(
    output_dir="./gemma-formatter-simple-fp16-checkpoints",
    num_train_epochs=3,  # Start with 3 epochs
    per_device_train_batch_size=1,  # Small batch for 1B model
    save_steps=4,
    save_total_limit=2,
    logging_steps=2,
    learning_rate=5e-5,  # Standard learning rate
    # fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
    # fp16=True,
)

# 6. Create data collator (handles padding)
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False  # mlm=False for causal language modeling
)

# 7. Create trainer and train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

print("Starting training...")
trainer.train()

# 8. Save the model
trainer.save_model("./gemma-formatter-simple-fp16")
tokenizer.save_pretrained("./gemma-formatter-simple-fp16")
print("Model saved!")

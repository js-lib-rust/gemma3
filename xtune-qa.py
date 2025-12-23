import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW
from typing import Dict, List

# --- Configuration ---
MODEL_NAME = "/home/irotaru/data/hugging-face/model/gemma-3-1b-it"  # Use the instruction-tuned version
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LEARNING_RATE = 2e-5  # A small learning rate is crucial for fine-tuning
EPOCHS = 3           # Very few epochs for a quick update
IGNORE_INDEX = -100  # Default value for CrossEntropyLoss masking

# --- Single Training Example (Validated User Feedback) ---
# Format: Prompt + Response. Use a chat template for best results.
# The model will learn to generate the "RESPONSE" tokens.
PROMPT = "Care este cel mai înalt vârf muntos din România?"
RESPONSE = "Cel mai înalt vârf muntos din România este Vârful Moldoveanu din Munții Făgărași, situat la o altitudine de 2544 metri. Se găsește în masivul Carpații de sud."
# Gemma 3 IT chat template (simplified for illustration):
TRAINING_TEXT = f"<bos><start_of_turn>user\n{PROMPT}<end_of_turn>\n<start_of_turn>model\n{RESPONSE}<end_of_turn><eos>"


# 1. Setup Model and Tokenizer (Full Precision)
# 16GB of VRAM should be sufficient for Gemma 1.1B in bfloat16 or float16/float32.
# We use torch.bfloat16 for modern NVIDIA GPUs (Compute Capability >= 8.0)
# or torch.float16 for older GPUs to save memory over float32.

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,  # Use bfloat16 for better numerical stability/memory efficiency
    device_map=DEVICE
)
model.train()
optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)

# --- 2. Data Preparation and Loss Masking ---
def tokenize_and_mask(text: str, response_start_token: str = "<start_of_turn>model\n") -> Dict[str, torch.Tensor]:
    """Tokenizes a prompt-completion example and creates a loss mask."""
    # A) Tokenize the full sequence
    tokenized = tokenizer(TRAINING_TEXT, return_tensors="pt", truncation=True, padding="max_length", max_length=512)
    input_ids = tokenized["input_ids"].to(DEVICE)
    attention_mask = tokenized["attention_mask"].to(DEVICE)

    # B) Create labels (which are just a copy of input_ids for Causal LM)
    # The Cross-Entropy Loss function (which is built into AutoModelForCausalLM's forward pass)
    # compares the logits for token 'i' against the label for token 'i+1'.
    labels = input_ids.clone()
    
    # C) Loss Masking (The core of instruction fine-tuning)
    # We want the model to only train on generating the 'RESPONSE' part.
    # Tokens corresponding to the PROMPT are set to IGNORE_INDEX (-100).
    response_start_index = TRAINING_TEXT.find(response_start_token)
    if response_start_index == -1:
        print("Warning: Response start token not found. Training on entire sequence.")
        
    # Find the token ID position where the response starts
    response_token_index = input_ids[0].size(0)
    for i in range(1, input_ids.size(1)):
        # Decode the tokens one by one until the text starts to match the response
        decoded_text = tokenizer.decode(input_ids[0][:i], skip_special_tokens=False)
        if decoded_text.endswith(response_start_token):
            response_token_index = i
            break
            
    # Set labels for all tokens *before* the start of the response to IGNORE_INDEX
    # This ensures the loss is only calculated on the "completion" tokens.
    labels[0, :response_token_index] = IGNORE_INDEX
    
    return {
        "input_ids": input_ids, 
        "attention_mask": attention_mask, 
        "labels": labels
    }

# --- 3. Single-Example Fine-Tuning Loop ---
tokenized_data = tokenize_and_mask(TRAINING_TEXT)
print(f"Starting training on device: {DEVICE}")
print(f"Number of trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad)/1e6:.2f}M")
print(f"Training for {EPOCHS} epoch(s)...")

for epoch in range(EPOCHS):
    optimizer.zero_grad()
    
    # Model forward pass
    # When you pass 'labels', the Hugging Face CausalLM model calculates the 
    # CrossEntropyLoss internally and returns it as the 'loss' attribute in the output.
    outputs = model(
        input_ids=tokenized_data["input_ids"],
        attention_mask=tokenized_data["attention_mask"],
        labels=tokenized_data["labels"]
    )
    
    loss = outputs.loss
    
    # Backward pass and optimization
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch+1}/{EPOCHS} Loss: {loss.item():.4f}")

# --- 4. Save the Fine-Tuned Model ---
output_dir = "gemma3-ft"
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"\nFine-tuning complete. Model saved to {output_dir}")


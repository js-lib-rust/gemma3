import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "function-270m"
device = "cuda:0" if torch.cuda.is_available() else "cpu"

prompt = """<bos><start_of_turn>developer
You are a model that can do function calling with the following functions<start_function_declaration>declaration:\
hera_describe_device{description:<escape>Create a detailed description of the requested device.<escape>,\
parameters:{properties:{device:{description:<escape>human-readable device name, unique per HERA.<escape>,\
type:<escape>STRING<escape>}},required:[<escape>device<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration>\
<start_function_declaration>declaration:hera_get_device_actions{description:<escape>Retrieves the actions supported by \
a device.<escape>,parameters:{properties:{device:{description:<escape>human-readable device name, unique per HERA.\
<escape>,type:<escape>STRING<escape>}},required:[<escape>device<escape>],type:<escape>OBJECT<escape>}}\
<end_function_declaration><start_function_declaration>declaration:hera_get_heating_state{description:<escape>Get \
central heating state.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration>\
<start_function_declaration>declaration:hera_list_devices{description:<escape>List all devices registered to HERA.\
<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:\
hera_read_humidity{description:<escape>Read current humidity.<escape>,parameters:{type:<escape>OBJECT<escape>}}\
<end_function_declaration><start_function_declaration>declaration:hera_read_sensors{description:<escape>Read all \
registered sensors.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration>\
<start_function_declaration>declaration:hera_read_temperature{description:<escape>Read the current temperature from \
devices in a specified zone.<escape>,parameters:{properties:{zone:{description:<escape>human-readable zone name of the \
location where the devices are placed.<escape>,type:<escape>STRING<escape>}},required:[<escape>zone<escape>],\
type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_run_diagnose{\
description:<escape>Check that a device is reachable and running properly. Return a diagnosis report.<escape>,\
parameters:{properties:{device:{description:<escape>human-readable device name, unique per HERA.<escape>,\
type:<escape>STRING<escape>}},required:[<escape>device<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration>\
<start_function_declaration>declaration:hera_start_heating{description:<escape>Start central heating.<escape>,\
parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:\
hera_stop_heating{description:<escape>Stop central heating.<escape>,parameters:{type:<escape>OBJECT<escape>}}\
<end_function_declaration><end_of_turn>
<start_of_turn>user
Read the temperature sensor in the living room.<end_of_turn>
<start_of_turn>model
"""

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16).to(device)

model.eval()

# Tokenize input
input_ids = tokenizer.encode(prompt, return_tensors="pt")
print(f"Input tokens: {tokenizer.convert_ids_to_tokens(input_ids[0])}")
print(f"Input token IDs: {input_ids[0]}")

generated = input_ids.to(device)
print(f"generated device: {generated.device}")
all_logits = []

with torch.no_grad():
    for step in range(30):
        # Forward pass
        outputs = model(generated)
        logits = outputs.logits[0, -1, :]  # Last token logits

        # Store for debugging
        all_logits.append(logits.clone())

        # Greedy selection
        next_token_id = torch.argmax(logits).item()

        # Check if it's EOS
        if next_token_id == tokenizer.eos_token_id:
            print(f"\nStep {step}: Selected EOS token")
            break

        # Append to sequence
        generated = torch.cat([generated, torch.tensor([[next_token_id]]).to(device=device)], dim=1)

        # Debug output
        token_str = tokenizer.decode([next_token_id])
        top_5_tokens = torch.topk(logits, 5)
        print(f"\nStep {step}:")
        print(f"  Selected: '{token_str}' (id={next_token_id})")
        print(f"  Top 5 tokens:")
        for i, (val, idx) in enumerate(zip(top_5_tokens.values, top_5_tokens.indices)):
            tok = tokenizer.decode([idx.item()])
            prob = F.softmax(val, dim=0).item()
            print(f"    {i + 1}. '{tok}' (id={idx.item()}) - logit: {val.item():.4f}, prob: {prob:.4f}")

# Decode final result
full_output = tokenizer.decode(generated[0], skip_special_tokens=False)
print(f"full_output: {full_output}")
# print(f"generated: {generated}")
# print(f"all_logits: {all_logits}")

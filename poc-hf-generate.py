import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

model_path = "function-270m"
device = "cuda:0"

prompt = """<bos><start_of_turn>developer
You are a model that can do function calling with the following functions<start_function_declaration>declaration:hera_describe_device{description:<escape>Create a detailed description of the requested device.<escape>,parameters:{properties:{device:{description:<escape>human-readable device name, unique per HERA.<escape>,type:<escape>STRING<escape>}},required:[<escape>device<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_get_device_actions{description:<escape>Retrieves the actions supported by a device.<escape>,parameters:{properties:{device:{description:<escape>human-readable device name, unique per HERA.<escape>,type:<escape>STRING<escape>}},required:[<escape>device<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_get_heating_state{description:<escape>Get central heating state.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_list_devices{description:<escape>List all devices registered to HERA.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_read_humidity{description:<escape>Read current humidity.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_read_sensors{description:<escape>Read all registered sensors.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_read_temperature{description:<escape>Read the current temperature from devices in a specified zone.<escape>,parameters:{properties:{zone:{description:<escape>human-readable zone name of the location where the devices are placed.<escape>,type:<escape>STRING<escape>}},required:[<escape>zone<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_run_diagnose{description:<escape>Check that a device is reachable and running properly. Return a diagnosis report.<escape>,parameters:{properties:{device:{description:<escape>human-readable device name, unique per HERA.<escape>,type:<escape>STRING<escape>}},required:[<escape>device<escape>],type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_start_heating{description:<escape>Start central heating.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><start_function_declaration>declaration:hera_stop_heating{description:<escape>Stop central heating.<escape>,parameters:{type:<escape>OBJECT<escape>}}<end_function_declaration><end_of_turn>
<start_of_turn>user
Read the temperature sensor in the living room.<end_of_turn>
<start_of_turn>model
"""

tokenizer = AutoTokenizer.from_pretrained(model_path, device=device)
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16, device_map=device)

def compare_generation_approaches(model, tokenizer, prompt):
    """Compare raw torch vs transformers generation"""

    print(f"{'=' * 60}")
    print(f"Prompt: '{prompt}'")
    print(f"{'=' * 60}")

    # 1. Raw torch approach (working)
    input_ids = tokenizer.encode(prompt, return_tensors='pt', device=device)
    print(f"\n🔧 RAW TORCH APPROACH:")
    print(f"Input IDs: {input_ids[0].tolist()}")

    with torch.no_grad():
        # Simple greedy generation
        generated = input_ids.clone().to(device=device)
        for _ in range(20):
            outputs = model(generated)
            next_token = torch.argmax(outputs.logits[0, -1, :]).unsqueeze(0).unsqueeze(0)
            if next_token.item() == tokenizer.eos_token_id:
                break
            generated = torch.cat([generated, next_token], dim=1)

        raw_output = tokenizer.decode(generated[0], skip_special_tokens=False)
        print(f"Output: '{raw_output}'")

    # 2. Transformers default generation
    print(f"\n🤗 TRANSFORMERS DEFAULT:")
    with torch.no_grad():
        transformers_output = model.generate(
            input_ids.to(device=device),
            max_new_tokens=20,
            do_sample=False,  # Force greedy
            temperature=1.0,
        )
        transformers_text = tokenizer.decode(transformers_output[0], skip_special_tokens=False)
        print(f"Output: '{transformers_text}'")

    # 3. Transformers with explicit GenerationConfig
    print(f"\n🤗 TRANSFORMERS WITH EXPLICIT CONFIG:")
    gen_config = GenerationConfig(
        max_new_tokens=20,
        do_sample=False,
        temperature=1.0,
        repetition_penalty=1.0,  # Explicitly disable
        no_repeat_ngram_size=0,  # Explicitly disable
        use_cache=True,
        pad_token_id=tokenizer.eos_token_id,  # Common culprit
    )

    with torch.no_grad():
        transformers_output = model.generate(
            input_ids.to(device=device),
            generation_config=gen_config,
        )
        transformers_text = tokenizer.decode(transformers_output[0], skip_special_tokens=False)
        print(f"Output: '{transformers_text}'")

    # 4. Check if pad_token is causing issues
    print(f"\n🔍 TOKENIZER CONFIG:")
    print(f"pad_token: {tokenizer.pad_token}")
    print(f"pad_token_id: {tokenizer.pad_token_id}")
    print(f"eos_token: {tokenizer.eos_token}")
    print(f"eos_token_id: {tokenizer.eos_token_id}")

    # 5. Try with explicit attention mask
    print(f"\n🤗 WITH EXPLICIT ATTENTION MASK:")
    attention_mask = torch.ones_like(input_ids).to(device=device)
    with torch.no_grad():
        transformers_output = model.generate(
            input_ids.to(device=device),
            attention_mask=attention_mask,
            max_new_tokens=20,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
        transformers_text = tokenizer.decode(transformers_output[0], skip_special_tokens=False)
        print(f"Output: '{transformers_text}'")


# Run comparison
compare_generation_approaches(model, tokenizer, "Read the temperature sensor in the living room.")


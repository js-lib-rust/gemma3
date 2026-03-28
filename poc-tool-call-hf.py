import time

import torch
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

for _ in range(4):
    start_time = time.time()
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
    with torch.no_grad():
        outputs = model.generate(input_ids, max_new_tokens=30, do_sample=False)
        text = tokenizer.decode(outputs[0], skip_special_tokens=False)
        print(f"text: '{text}'")
    print(f"generation time {time.time() - start_time} sec.")
    print()
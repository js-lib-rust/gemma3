import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import os

model_dir = os.environ.get("AI_MODEL_DIR") 
model_path = model_dir + "/hugging-face/model/gemma-3-270m-it"
model_path = "./formatter-270m"

tokenizer = AutoTokenizer.from_pretrained(model_path)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16)
# model = AutoModelForCausalLM.from_pretrained(model_path)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()
print(f"Model loaded on {device}")

system_prompt = "Respond to the next user prompt using provided function response."
user_prompt = "please list all health measurements"
user_prompt = "display today health measurements in table format"
#user_prompt = "display my health measurements for today, in a table format"
#user_prompt = "list today measurements related to circulatory system"
#user_prompt = "create health measurements from today readings"
#user_prompt = "analyse bmi from today readings"
#user_prompt = "is my bmi value in normal range. how can it be classified"
#user_prompt = "interpret body mass index from today health readings"
# user_prompt = "create comprehensible and detailed medical report from today health readings; please include measurement units and medical opinion"
#user_prompt = "create medical report from today health readings"
# user_prompt = "what is today pulse pressure value"
#user_prompt = "what is my body temperature"
# user_prompt = "show me my morning and evening blood pressure"
#user_prompt = "is the central heating on?"
# user_prompt = "please tell me the status of the central heating"
# user_prompt = "save blood glucose 101 to medical archive"
# user_prompt = "save glucose 101"
function_response = """{"timestamp":"2025-12-17 08:47:02","person":"Iulian Rotaru","measurement":"systolic_pressure","value":124}
{"timestamp":"2025-12-17 08:47:03","person":"Iulian Rotaru","measurement":"diastolic_pressure","value":81}
{"timestamp":"2025-12-17 08:47:04","person":"Iulian Rotaru","measurement":"pulse_pressure","value":43}
{"timestamp":"2025-12-17 08:47:05","person":"Iulian Rotaru","measurement":"heart_rate","value":72}
{"timestamp":"2025-12-17 08:48:58","person":"Iulian Rotaru","measurement":"body_temperature","value":35.4}
{"timestamp":"2025-12-20 08:53:55","person":"Iulian Rotaru","measurement":"blood_glucose","value":101.0}
{"timestamp":"2025-12-17 08:49:26","person":"Iulian Rotaru","measurement":"body_weight","value":89.5}
{"timestamp":"2025-12-17 08:49:27","person":"Iulian Rotaru","measurement":"body_mass_index","value":28.89}
{"timestamp":"2025-12-17 08:49:28","person":"Iulian Rotaru","measurement":"height","value":1.76}
{"timestamp":"2025-12-17 08:49:29","person":"Iulian Rotaru","measurement":"head_circumference","value":65}
{"timestamp":"2025-12-17 08:49:29","person":"Iulian Rotaru","measurement":"intelligence_quotient","value":105}
"""

# function_response = """{"timestamp":"2025-12-22 13:53:55","person":"Iulian Rotaru","measurement":"blood_glucose","value":101.0}"""
# function_response = """{"setpoint":10.00,"hysteresis":0.00,"temperature":21.75,"running":false}"""

# Format the input exactly like during training
# input_text = f"{system_prompt}\n\nUser Prompt: {user_prompt}\n\nFunction Response:\n{function_response}\n\nAssistant Response:"

chat = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"User Prompt: {user_prompt}\nFunction Response: {function_response}"}
    #{"role": "user", "content": "what is the length of the danube river and were is reach the sea"}
    #{"role": "user", "content": "what is the length of the nile river"}
    #{"role": "user", "content": "what is the height of mount everest"}
    #{"role": "user", "content": "display 1, 2, 3 in table format"}
]

input_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
print(input_text)
inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=4000)
inputs = {k: v.to(device) for k, v in inputs.items()}

print("Generating response...")
streamer = TextStreamer(tokenizer)
config = {
    'max_new_tokens': 500,
    'do_sample': True,
    'pad_token_id': tokenizer.eos_token_id,
    #'streamer': streamer
}
for _ in range(10):
    with torch.no_grad():
        outputs = model.generate(**inputs, **config)
    input_length = inputs["input_ids"].shape[1]
    response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
    print(response)


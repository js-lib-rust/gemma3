import argparse
import os
import time

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer, BitsAndBytesConfig,
)

model_dir = os.environ.get("AI_MODEL_DIR")
base_model = model_dir + "/hugging-face/model/translategemma-4b-it"

tokenizer = AutoTokenizer.from_pretrained(base_model)

quantization = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    device_map="cuda:0",
    dtype=torch.bfloat16,
    quantization_config=quantization)

text = """# Functional Description 
The FSMS server retrieves work orders from specific SAP modules. Prior to operation, 
the server is configured by business consultants and coordination center dispatchers. Since administration is 
performed via a back-office application, these users—including members of the FSMS support team—are collectively 
referred to as "back-office operators."

Using the Data Transform Layer (DTL), the FSMS server generates the actions required to fulfill each work order based 
on specific attributes and business rules. While a single action is typically created per work order, the DTL can be 
configured to generate multiple actions for more complex requirements. Note that "DTL" is a proprietary Globema 
abstraction and should not be confused with "Data Transform Language" used in XML processing.

Each action inherits its location from its parent work order. The FSMS server then assigns these actions to a 
specific center based on the action's location and the geographical area configured for that coordination center. 
Dispatchers then assign these actions to field teams using a Gantt chart, taking into account team types, schedules, 
and skill sets. To maximize efficiency, dispatchers must also sequence actions to minimize travel time between 
locations.

The FSMS server includes an optimizer capable of automated assignment, though its frequency of use is undocumented; 
it likely utilizes a shortest-path algorithm implementation. Similarly, the OMS system generates tickets that are 
processed by the FSMS server through the same workflow: converting tickets into actions, then assigning and 
sequencing them as described above.

In addition to orders, back-office operators can manually create actions directly within the FSMS server; these are 
known as "FFA Actions." Once created, FFA actions follow the standard processing workflow."""

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "source_lang_code": "en",
                "target_lang_code": "ro",
                "text": text,
            }
        ],
    }
]

start_time = time.time()
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
model.generate(**model_inputs, max_new_tokens=1000, streamer=streamer)
print(f"Text generation time: {time.time() - start_time}")

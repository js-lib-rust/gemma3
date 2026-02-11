from aiohttp import web
import time
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer
)

MODEL_PATH = "rewrite-270m"
DEVICE = 'cuda:0'

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map=DEVICE)


async def handle_slm_request(request):
    try:
        request_start_time = time.time()

        json_request = await request.json()
        system = "Classify and rewrite next user prompt"
        prompt = json_request['prompt']
        print(f'prompt: {prompt}')

        chat = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        chat_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        print(f"chat_text: {chat_text}")
        inputs = tokenizer([chat_text], return_tensors="pt").to(model.device)

        config = {
            'max_new_tokens': 400,
            'do_sample': False,
            'num_beams': 1,
            'pad_token_id': tokenizer.eos_token_id,
        }
        print(f"config: {config}")
        outputs = model.generate(**inputs, **config)
        input_length = inputs["input_ids"].shape[1]
        output_text = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
        print(f"output_text: {output_text}")

        output_parts = output_text.split(": ")
        response = {"agent": f"{output_parts[0]}", "prompt": f"{output_parts[1]}"}
        print(f"Request processing time: {time.time() - request_start_time}")
        return web.json_response(response, status=200)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


app = web.Application()
app.router.add_post('/', handle_slm_request)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=1966, access_log=None)

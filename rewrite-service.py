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
            'return_dict_in_generate': True,
            'output_scores': True
        }
        print(f"config: {config}")
        outputs = model.generate(**inputs, **config)
        generated_ids = outputs.sequences[0][inputs["input_ids"].shape[1]:]

        transition_scores = model.compute_transition_scores(outputs.sequences, outputs.scores, normalize_logits=True)
        token_probs = transition_scores[0].exp().cpu().numpy()
        avg_confidence = float(token_probs.mean())
        min_confidence = float(token_probs.min())

        output_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
        print(f"output_text: {output_text}")
        print(f"confidence: {avg_confidence:.4f} (min: {min_confidence:.4f})")

        output_parts = output_text.split(": ")
        response = {
            "agent": f"{output_parts[0]}",
            "prompt": f"{output_parts[1]}",
            "confidence": avg_confidence,
            "confidence_min": min_confidence
        }
        print(f"response: {response}")
        
        print(f"Request processing time: {time.time() - request_start_time}")
        return web.json_response(response, status=200)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


app = web.Application()
app.router.add_post('/', handle_slm_request)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=1966, access_log=None)

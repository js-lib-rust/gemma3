import argparse

import torch
from aiohttp import web
import time
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer
)

import util

parser = argparse.ArgumentParser()
parser.add_argument("--model", action="store", type=str, default="router-270m")
parser.add_argument("--dtype", action="store", type=util.dtype, default="float32")
args = parser.parse_args()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
model_path = util.get_model_path(args.model) if args.model.startswith('/') else args.model
print(f"Use device {device}")
print(f"Use model {model_path}")
print(f"Use dtype {args.dtype}")

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=args.dtype, device_map=device)


async def handle_slm_request(request):
    try:
        request_start_time = time.time()

        json_request = await request.json()
        system = "Rewrite and route the next user prompt"
        prompt = json_request['prompt']
        print(f'prompt: {prompt}')

        chat = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        chat_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        print(f"chat_text: {chat_text}")
        inputs = tokenizer([chat_text], return_tensors="pt").to(model.device)

        max_new_tokens = int(json_request.get('max_new_tokens', "400"))
        do_sample = bool(json_request.get('do_sample'))
        num_beams = int(json_request.get('num_beams', "1"))
        config = {
            'max_new_tokens': max_new_tokens,
            'do_sample': do_sample,
            'num_beams': num_beams,
            'pad_token_id': tokenizer.eos_token_id,
            'return_dict_in_generate': True,
            'output_scores': True
        }
        if num_beams > 1:
            config['num_return_sequences'] = num_beams
        print(f"config: {config}")

        outputs = model.generate(**inputs, **config)
        generated_ids = outputs.sequences
        transition_scores = model.compute_transition_scores(outputs.sequences, outputs.scores, normalize_logits=True)

        response = []
        for sequence_index in range(len(generated_ids)):
            sequence_generated_ids = generated_ids[sequence_index][inputs["input_ids"].shape[1]:]

            sequence_transition_scores = transition_scores[sequence_index]
            token_probs = sequence_transition_scores.exp().cpu().numpy()
            avg_confidence = float(token_probs.mean())
            min_confidence = float(token_probs.min())

            output_text = tokenizer.decode(sequence_generated_ids, skip_special_tokens=True)
            print(f"output_text: {output_text}")
            print(f"confidence: {avg_confidence:.4f} (min: {min_confidence:.4f})")

            # agent1:prompt1\nagent2:prompt2\nagent3:prompt3
            actions = []
            for line in output_text.split("\n"):
                line_parts = line.split(":", 1)
                actions.append({"agent": f"{line_parts[0]}", "prompt": f"{line_parts[1]}"})

            response.append({
                "actions": actions,
                "confidence": avg_confidence,
                "confidence_min": min_confidence
            })

        print(f"response: {response}")
        print(f"Request processing time: {time.time() - request_start_time}")
        return web.json_response(response, status=200)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


app = web.Application()
app.router.add_post('/', handle_slm_request)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=1966, access_log=None)

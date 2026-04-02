import argparse
import json
import os.path

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
parser.add_argument("--port", action="store", type=int, default=1966)
args = parser.parse_args()

device = "cuda:0" if torch.cuda.is_available() else "cpu"
model_path = util.get_model_path(args.model) if args.model.startswith('/') else args.model
print(f"Use device {device}")
print(f"Use model {model_path}")
print(f"Use dtype {args.dtype}")
print(f"Use port {args.port}")

tokenizer = AutoTokenizer.from_pretrained(model_path)
util.patch_tokenizer(tokenizer)
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=args.dtype, device_map=device)


async def handle_slm_request(request):
    try:
        request_start_time = time.time()

        json_request = await request.json()
        tools = json_request.get('tools', None)
        if tools:
            tools_path = os.path.abspath(f"data/tool/{tools}.tools.hf.json")
            print(f"Loading tools {tools_path}")
            with open(tools_path, 'r', encoding='UTF-8') as file:
                tools = json.load(file)
            system_role = "developer"
            system = "You are a model that can do function calling with the following functions"
        else:
            system_role = "system"
            system = "Rewrite and route the next user prompt"
        prompt = json_request['prompt']
        min_new_tokens = int(json_request.get('min_new_tokens', "1"))
        max_new_tokens = int(json_request.get('max_new_tokens', "400"))
        do_sample = bool(json_request.get('do_sample'))
        num_beams = int(json_request.get('num_beams', "1"))
        repetition_penalty = float(json_request.get('repetition_penalty', "1.0"))
        no_repeat_ngram_size = int(json_request.get('no_repeat_ngram_size', "0"))
        temperature = float(json_request.get('temperature', "1.0"))

        print(f'system_role: {system_role}')
        print(f'system: {system}')
        print(f'tools: {tools}')
        print(f'prompt: {prompt}')
        print(f'max_new_tokens: {max_new_tokens}')
        print(f'do_sample: {do_sample}')
        print(f'num_beams: {num_beams}')
        print(f'repetition_penalty: {repetition_penalty}')

        chat = [{"role": system_role, "content": system}, {"role": "user", "content": prompt}]
        chat_text = tokenizer.apply_chat_template(chat, tools=tools, tokenize=False, add_generation_prompt=True)
        print(f"chat_text: {chat_text}")
        inputs = tokenizer([chat_text], return_tensors="pt").to(model.device)

        config = {
            'min_new_tokens': min_new_tokens,
            'max_new_tokens': max_new_tokens,
            'do_sample': do_sample,
            'temperature': temperature,
            'num_beams': num_beams,
            'num_return_sequences': num_beams,
            'pad_token_id': tokenizer.eos_token_id,
            'return_dict_in_generate': True,
            'output_scores': True,
            'repetition_penalty': repetition_penalty,
            'no_repeat_ngram_size': no_repeat_ngram_size
        }
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

            if tools:
                # <start_function_call>call:hera_read_temperature{zone:<escape>living room<escape>}<end_function_call>
                function_call = output_text[0]
                if not function_call.startswith("<start_function_call>call:"):
                    function = {
                        "agent": "unknown",
                        "name": "unknown",
                        "arguments": {}
                    }
                else:
                    function = util.parse_gemma_function_response(output_text)[0]

                response.append({
                    "function": function,
                    "confidence": avg_confidence,
                    "confidence_min": min_confidence
                })
            else:
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
    except BaseException as e:
        return web.json_response({"error": str(e)}, status=500)


app = web.Application()
app.router.add_post('/', handle_slm_request)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=args.port, access_log=None)

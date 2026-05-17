import argparse
import asyncio
import struct
import time

import orjson
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, DynamicCache

import util

parser = argparse.ArgumentParser()
parser.add_argument("--device", action="store", type=str, default="cuda:0")
parser.add_argument("--model", action="store", type=str, default="router-270m")
parser.add_argument("--dtype", action="store", type=util.dtype, default="bfloat16")
parser.add_argument("--port", action="store", type=int, default=1965)
args = parser.parse_args()

device = args.device if torch.cuda.is_available() else "cpu"
model_path = util.get_model_path(args.model) if args.model.startswith('/') else args.model
print(f"Use device {device}")
print(f"Use model {model_path}")
print(f"Use dtype {args.dtype}")
print(f"Use port {args.port}")

tokenizer = AutoTokenizer.from_pretrained(model_path)
util.patch_tokenizer(tokenizer)
model = AutoModelForCausalLM.from_pretrained(model_path, dtype=args.dtype, device_map=device)


async def send_json(writer, data):
    payload = orjson.dumps(data)
    length = len(payload)
    # pack length as 4-byte big endian + payload
    writer.write(struct.pack('>I', length) + payload)
    await writer.drain()


def route_prompt(prompt):
    request_start_time = time.time()

    system = "Rewrite and route the next user prompt"
    chat = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
    chat_text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    print(f"chat_text: {chat_text}")
    inputs = tokenizer([chat_text], return_tensors="pt").to(model.device)

    past_key_values = DynamicCache(config=model.config)
    config = {
        'min_new_tokens': 1,
        'max_new_tokens': 400,
        'do_sample': False,
        'temperature': 1.0,
        'num_beams': 1,
        'num_return_sequences': 1,
        'pad_token_id': tokenizer.eos_token_id,
        'return_dict_in_generate': True,
        'output_scores': True,
        'repetition_penalty': 1.0,
        'no_repeat_ngram_size': 0,
        'past_key_values': past_key_values
    }
    print(f"config: {config}")

    outputs = model.generate(**inputs, **config)
    generated_ids = outputs.sequences
    transition_scores = model.compute_transition_scores(outputs.sequences, outputs.scores, normalize_logits=True)

    sequence_generated_ids = generated_ids[0][inputs["input_ids"].shape[1]:]

    sequence_transition_scores = transition_scores[0]
    token_probs = sequence_transition_scores.exp().cpu().numpy()
    avg_confidence = float(token_probs.mean())
    min_confidence = float(token_probs.min())

    output_text = tokenizer.decode(sequence_generated_ids, skip_special_tokens=True)
    print(f"output_text: {output_text}")
    print(f"confidence: {avg_confidence:.4f} (min: {min_confidence:.4f})")
    processing_time = time.time() - request_start_time
    print(f"processing_time: {processing_time}")
    return output_text, avg_confidence, processing_time


class SocketServer:
    def __init__(self, host='0.0.0.0', port=args.port, timeout=15.0):
        self.host = host
        self.port = port
        self.timeout = timeout  # If no message in 15s, drop client

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"[*] New connection from {addr}")

        try:
            while True:
                try:
                    # 1. Read the 4-byte length header
                    # Use wait_for to implement the heartbeat timeout
                    header = await asyncio.wait_for(reader.readexactly(4), timeout=self.timeout)
                    length = struct.unpack('>I', header)[0]

                    # 2. Read the payload
                    payload = await asyncio.wait_for(reader.readexactly(length), timeout=self.timeout)
                    message = orjson.loads(payload)

                    # 3. Handle Message Types
                    msg_type = message.get("type")

                    if msg_type == "ping":
                        print(f"[{addr}] Ping received. Sending Pong.")
                        await send_json(writer, {"type": "pong"})

                    elif msg_type == "request":
                        print(f"[{addr}] Data received: {message.get('payload')}")
                        prompt = message.get('payload').get('prompt')
                        print(f"prompt: {prompt}")
                        text, confidence, duration = route_prompt(prompt)
                        await send_json(writer, {"type": "response", "text": text, "confidence": confidence,
                                                 "duration": duration})

                    else:
                        print(f"[{addr}] Unknown message type: {msg_type}")

                except asyncio.TimeoutError:
                    print(f"[!] {addr} timed out (no heartbeat/data). Closing.")
                    break
                except asyncio.IncompleteReadError:
                    print(f"[*] {addr} disconnected.")
                    break

        except Exception as e:
            print(f"[!] Error handling {addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"[*] Connection with {addr} closed.")

    async def run(self):
        async_server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"[*] Server listening on {self.host}:{self.port}")
        async with async_server:
            await async_server.serve_forever()


if __name__ == "__main__":
    server = SocketServer()
    asyncio.run(server.run())

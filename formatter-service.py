from threading import Event
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer,
    DynamicCache,
    BitsAndBytesConfig
)
import torch
import signal
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import subprocess
import os

base_model = "formatter-270m"
device = 'cuda:0'
history = []

tokenizer = AutoTokenizer.from_pretrained(base_model)
terminators = [tokenizer.eos_token_id]
model = AutoModelForCausalLM.from_pretrained(base_model, device_map=device, dtype=torch.float32)


class StreamerWriter(TextStreamer):
    def __init__(self, _tokenizer, _writer):
        super(StreamerWriter, self).__init__(_tokenizer, skip_prompt=True)
        self.writer = _writer
        self.response = ""

    def on_finalized_text(self, text, stream_end=False):
        text = re.sub('<end_of_turn>', '', text)
        if stream_end:
            text = text.replace(tokenizer.eos_token, '')

        if text:
            data = text.encode('utf-8')
            self.response += text

            self.writer.write(f'{len(data):x}\r\n'.encode('utf-8'))
            self.writer.write(data)
            self.writer.write('\r\n'.encode('utf-8'))
            self.writer.flush()

        if stream_end:
            self.writer.write('0\r\n\r\n'.encode('utf-8'))


class StreamerWithSpeedDisplay(StreamerWriter):
    def __init__(self, _tokenizer, _writer, display_interval=5):
        super().__init__(_tokenizer, _writer)
        self.token_count = 0
        self.start_time = None
        self.last_display_time = None
        self.display_interval = display_interval
        self.last_token_time = None

    def put(self, value):
        current_time = time.time()

        if self.start_time is None:
            self.start_time = current_time
            self.last_display_time = current_time
            self.last_token_time = current_time

        self.token_count += 1

        # Display speed at intervals
        if current_time - self.last_display_time >= self.display_interval:
            elapsed = current_time - self.start_time
            speed = self.token_count / elapsed
            print(f"\n[Speed: {speed:.1f} tokens/s | Tokens: {self.token_count} | Time: {elapsed:.1f}s]",
                  end='', flush=True)
            self.last_display_time = current_time

        self.last_token_time = current_time

        # Call parent
        super().put(value)

    def end(self):
        super().end()

        if self.start_time and self.token_count > 0:
            total_time = time.time() - self.start_time
            avg_speed = self.token_count / total_time
            print(f"\n\n=== Final Statistics ===")
            print(f"Total tokens: {self.token_count}")
            print(f"Total time: {total_time:.2f}s")
            print(f"Average speed: {avg_speed:.2f} tokens/s")
            print(f"Throughput: {(avg_speed * 60):.0f} tokens/min")


class RequestHandler(BaseHTTPRequestHandler):  # type: ignore
    protocol_version = 'HTTP/1.1'

    def do_POST(self):
        print(f'do_POST: self.path: {self.path}')
        if self.path == '/':
            self.do_SLM_request()
        else:
            self.send_error(404, "Endpoint not found")

    def do_SLM_request(self):
        global tokenizer, terminators, model
        request_start_time = time.time()

        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        request = json.loads(body)

        system = request['system']
        print(f'system: {system}')
        profile = request['profile']
        print(f'profile: {profile}')
        settings = request['settings']
        print(f'settings: {settings}')
        context = request['context']
        print(f'context: {context}')
        prompt = request['prompt']
        print(f'prompt: {prompt}')
        use_temperature = request['use_temperature']
        print(f'use_temperature: {use_temperature}')
        use_history = request['use_history']
        print(f'use_history: {use_history}')

        system_content = []
        if system:
            system_content.append(system)
        if profile:
            system_content.append(f"User Profile:\n{profile}")
        if settings:
            system_content.append(f"Current Settings:\n{settings}")

        chat = []
        if system_content:
            chat.append({"role": "system", "content": "\n\n".join(system_content)})
        if use_history and not context:
            for conversation in history:
                chat.append({"role": "user", "content": conversation[0]})
                chat.append({"role": "assistant", "content": conversation[1]})
        chat.append({"role": "user", "content": prompt})
        text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        print(f"text: {text}")
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        streamer = StreamerWithSpeedDisplay(tokenizer, self.wfile)
        past_key_values = DynamicCache(config=model.config)
        generate_config = {
            'max_new_tokens': 2_000,
            'do_sample': False,
            'streamer': streamer,
            'use_cache': True,
            'past_key_values': past_key_values,
        }
        if not use_temperature:
            print('configure text generation without temperature')
            generate_config['temperature'] = 1.0
            generate_config['num_beams'] = 1
            generate_config['top_k'] = 1
            generate_config['top_p'] = 1.0
        print("generate_config: ", generate_config)
        _ = model.generate(**model_inputs, **generate_config)

        if use_history:
            history.append((prompt, streamer.response))
        print(f"Request processing time: {time.time() - request_start_time}")


class AppServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_serving = Event()

    def serve_forever(self, poll_interval=0.5):
        while not self.stop_serving.is_set():
            self.handle_request()

    def shutdown(self):
        print("Shutting down server gracefully...")
        self.stop_serving.set()
        self.server_close()


def signal_handler(signum, _frame, server):
    print(f"Received signal {signum}, shutting down gracefully...")
    server.shutdown()


if __name__ == '__main__':
    port = 1965
    server_address = ('0.0.0.0', port)
    httpd = AppServer(server_address, RequestHandler)
    print(f"Starting HTTP server on port {port}...")

    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, httpd))
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, httpd))

    httpd.serve_forever()

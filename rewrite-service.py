import json
import signal
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Event

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer
)

base_model = "rewrite-270m"
device = 'cuda:0'

tokenizer = AutoTokenizer.from_pretrained(base_model)
model = AutoModelForCausalLM.from_pretrained(base_model, device_map=device)


class RequestHandler(BaseHTTPRequestHandler):  # type: ignore
    protocol_version = 'HTTP/1.0'

    def do_POST(self):
        print(f'do_POST: self.path: {self.path}')
        if self.path == '/':
            self.do_SLM_request()
        else:
            self.send_error(404, "Endpoint not found")

    def do_SLM_request(self):
        global tokenizer, model
        request_start_time = time.time()

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        request = json.loads(body)

        system = "Classify and rewrite next user prompt"
        prompt = request['prompt']
        print(f'prompt: {prompt}')

        chat = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        print(f"text: {text}")
        inputs = tokenizer([text], return_tensors="pt").to(model.device)

        config = {
            'max_new_tokens': 200,
            'do_sample': False,
            'pad_token_id': tokenizer.eos_token_id,
        }
        print("generate_config: ", config)
        outputs = model.generate(**inputs, **config)
        input_length = inputs["input_ids"].shape[1]
        text = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
        print(f"text: {text}")

        body = bytes(text, 'UTF-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        self.wfile.write(body)
        self.wfile.flush()

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
    port = 1966
    server_address = ('0.0.0.0', port)
    httpd = AppServer(server_address, RequestHandler)
    print(f"Starting HTTP server on port {port}...")

    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, httpd))
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, httpd))

    httpd.serve_forever()

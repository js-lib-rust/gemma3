from threading import Event

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer,
)
import torch
import signal
import time

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

base_model = "/home/irotaru/data/hugging-face/model/gemma-3-4b-it"
device = 'cuda:0'

tokenizer = AutoTokenizer.from_pretrained(base_model)
terminators = [tokenizer.eos_token_id]
model = AutoModelForCausalLM.from_pretrained(base_model, device_map=device, dtype=torch.bfloat16)

prompt_template = """
<start_of_turn>user
You are an expert Q&A assistant. Your answer must be based only on the provided context. If a relation is missing from \
context do not try to infer it. Please generate elaborated, complete and nicely crafted responses, always using \
markdown; if response is a list always create markdown table with all avaible columns. If the context does not contain \
the answer, state that you 'cannot answer based on the provided documents'.

Context:
---
{context}
---

Question: {question}
<end_of_turn>
<start_of_turn>model
"""


class StreamerWriter(TextStreamer):
    def __init__(self, _tokenizer, _writer):
        super(StreamerWriter, self).__init__(_tokenizer, skip_prompt=True)
        self.writer = _writer
        self.text_heading = False

    def on_finalized_text(self, text, stream_end=False):
        # skip text heading that contains assistant metadata
        if self.text_heading:
            if text and text[0] == '<':
                self.text_heading = False
            return

        # remove end of text token
        if stream_end:
            text = text.replace(tokenizer.eos_token, '')

        if text:
            data = text.encode('utf-8')
            self.writer.write(f'{len(data):x}\r\n'.encode('utf-8'))
            self.writer.write(data)
            self.writer.write('\r\n'.encode('utf-8'))
            self.writer.flush()

        if stream_end:
            self.writer.write('0\r\n\r\n'.encode('utf-8'))


class RequestHandler(BaseHTTPRequestHandler):  # type: ignore
    protocol_version = 'HTTP/1.1'
    
    def do_GET(self):
        global tokenizer, terminators, model
        request_start_time = time.time()

        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.send_header('Transfer-Encoding', 'chunked')
        self.end_headers()

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        request = json.loads(body)
        context = request['context']
        question = request['question']
        print(f'context: {context}, question: {question}')

        with open(context + '.md', 'r') as file:
            context = file.read()

        prompt = prompt_template.format(context=context, question=question)
        prompt = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        streamer = StreamerWriter(tokenizer, self.wfile)
        _ = model.generate(**model_inputs, max_new_tokens=131_072, streamer=streamer)
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
    port = 1964
    server_address = ('0.0.0.0', port)
    httpd = AppServer(server_address, RequestHandler)
    print(f"Starting HTTP server on port {port}...")

    signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, httpd))
    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, httpd))

    httpd.serve_forever()


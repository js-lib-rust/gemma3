from threading import Event

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextStreamer,
    DynamicCache
)
import torch
import signal
import time

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re

base_model = "/home/irotaru/data/hugging-face/model/gemma-3-4b-it"
device = 'cuda:0'

tokenizer = AutoTokenizer.from_pretrained(base_model)
terminators = [tokenizer.eos_token_id]
model = AutoModelForCausalLM.from_pretrained(base_model, device_map=device, dtype=torch.bfloat16)

rag_system = "You are a contextual questions answering agent that only uses provided context and formats responses in markdown."

rag_template = """
Based on this context:
{context}

Answer: {question}

Remember: Only use provided context, do not try to infer missing information and use markdown formatting.
"""

#Remember: Only use provided context, use markdown formatting and create tables for lists, but only if list contains more than one item.

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
        text = re.sub(r'<.+?>', '', text)

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
    
    def do_POST(self):
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
        context = request['context']
        prompt = request['prompt']
        print(f'system: {system}, context: {context}, prompt: {prompt}')

        # for now, context is used only for RAG
        if context:
            with open(context + '.md', 'r') as file:
                context = file.read()
            prompt = rag_template.format(context=context, question=prompt)
            if not system:
                system = rag_system

        chat = []
        if system:
            chat.append({"role": "system", "content": system})
        chat.append({"role": "user", "content": prompt})
        text = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        print(f"text: {text}")
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        streamer = StreamerWriter(tokenizer, self.wfile)
        past_key_values = DynamicCache(config=model.config)
        _ = model.generate(**model_inputs, max_new_tokens=131_072, streamer=streamer, do_sample=False, use_cache=True, past_key_values=past_key_values)
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


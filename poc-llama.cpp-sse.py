import time

import requests
import json

model_url = "http://jarvis.local/v1/chat/completions"
enable_streaming = True

payload = {
    "model": "gemma-4-26B-A4B-Q5_K_M.gguf",  # model name is not used by llama.cpp
    "messages": [
        {"role": "system", "content": "Rewrite and route the next user prompt"},
        {"role": "user", "content": "save my body weight of 88"}],
    "stream": enable_streaming
}

session = requests.Session()
for _ in range(1):
    start_time = time.time()
    # use stream=True in the requests call to handle the incoming SSE stream
    response = session.post(model_url, json=payload, stream=enable_streaming)
    if not enable_streaming:
        print(response.json())

    for line in response.iter_lines():
        if not line:
            continue
        line_str = line.decode('utf-8')
        if not line_str.startswith('data: '):
            continue

        # remove the "data: " prefix from the SSE stream
        content_str = line_str[6:]
        if content_str == "[DONE]":
            break

        data = json.loads(content_str)
        # data: {"choices":[{"finish_reason":null,"index":0,"delta":{"content":"}."}}],"created":1777533835,
        # "id":"chatcmpl-pMKqBJ55YvKScilGmVJlnsGUmW3Scs31","model":"router-270m-q4_k_m.gguf",
        # "system_fingerprint":"b8961-f42e29fdf","object":"chat.completion.chunk"}
        delta = data['choices'][0]['delta'].get('content', '')
        if delta:
            print(delta, end='', flush=True)

    print()
    print()
    print(f"Llama.cpp server request processing time: {time.time() - start_time} sec.")

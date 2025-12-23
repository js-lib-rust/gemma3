import transformers
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM

import torch

model_id = "/home/irotaru/data/hugging-face/model/gemma-3-1b-it"
model_ft = 'gemma3-ft'

device = 'cuda:0'
num_epochs = 1
learning_rate = 5e-6
top_k = 20

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.bfloat16).to(device)
print(f'model parameters: {model.num_parameters():,}')

question = """<bos><start_of_turn>user
Question: Care este cel mai înalt vârf muntos din România?<end_of_turn>"""

answer = """<start_of_turn>model
Cel mai înalt vârf muntos din România este Vârful Moldoveanu din Munții Făgărași, situat la o altitudine de 2544 metri. Se găsește în masivul Carpații de sud.<end_of_turn><eos>"""

input_token_ids = tokenizer.encode(question, add_special_tokens=False, return_tensors='pt').to(device)
answer_token_ids = tokenizer.encode(answer, add_special_tokens=False, return_tensors='pt').to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
loss_function = torch.nn.CrossEntropyLoss()

for expected_token_id in answer_token_ids[0]:
    for epoch in range(num_epochs):
        print(f'epoch: {epoch}')
        optimizer.zero_grad()
        outputs = model.forward(input_token_ids)

        output_logits = outputs.logits[0]
        last_token_logits = output_logits[-1].to(device)
        next_token_id = last_token_logits.argmax()

        if expected_token_id == next_token_id:
            input_token_ids = torch.cat((input_token_ids, next_token_id.reshape((1, 1))), dim=1)
            text_parts = tokenizer.batch_decode(input_token_ids, skip_special_tokens=False)
            print(''.join(text_parts))
            print('break')
            break

        print(f'expected token:{tokenizer.decode(expected_token_id)} - predicted tokens:{tokenizer.batch_decode(last_token_logits.topk(top_k).indices)}')

        label = torch.zeros(len(last_token_logits)).to(device)
        label[expected_token_id] = 1
        loss = loss_function(last_token_logits, label)
        print(f'epoch: {epoch}, loss: {loss}')

        loss.backward()
        optimizer.step()

print()

print(f'Saving fine-tunned model {model_id} to {model_ft}...')
model.save_pretrained(model_ft, from_pt=False)
tokenizer.save_pretrained(model_ft)


import os
import json


def jsonl_to_train_hf(jsonl_file):
    dataset = []
    with open(jsonl_file, 'r', encoding='UTF-8') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('/*'):
                sample = json.loads(line)

                turns = [{"role": "system", "content": "Route and rewrite the next user prompt"}]
                for turn in sample:
                    turns.append({"role": "user", "content": turn["user"]})
                    turns.append({"role": "model", "content": turn['model']})
                dataset.append(turns)
    return dataset
    # print(json.dumps(hf_dataset, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("build router train set")

    dataset = []
    for f in os.listdir('.'):
        if f.endswith('.jsonl'):
            print(f"processing file {f}")
            dataset.extend(jsonl_to_train_hf(f))

    with open("router.train.hf.json", 'w', encoding='UTF-8') as file:
        json.dump(dataset, file, indent=2, ensure_ascii=False)

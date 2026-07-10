# Function Model
Instructions to build and evaluate function model.

## Datasets

### Tools Definitions

```shell
python dataset.py --task hf_tool_schema --tool health --file tool/health.tools.hf.json
```

### Tools Training

```shell
python dataset.py --task hf_function_set --file tool/health.train.jsonl --use-function-model
```


## Training

First fine tune function gemma base model to hera:

```shell
python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 1e-5 --files tool/home-automation.train.hf.json --tools tool/hera.tools.hf.json --model /functiongemma-270m-it --output-dir hera-270m --eval-steps 50 --save-steps 1000 --assert-max-length
```

Then continue hera fine-tuning with health agent:

```shell
python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 1e-5 --files tool/health.train.hf.json --tools tool/health.tools.hf.json --model hera-270m --output-dir hera-270m --eval-steps 50 --save-steps 1000 --assert-max-length
```

```shell
python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 8e-6 --files tool/home-automation.train.hf.json,tool/health.train.hf.json --tools tool/hera.tools.hf.json,tool/health.tools.hf.json --model /functiongemma-270m-it --output-dir function-270m --eval-steps 50 --save-steps 1000 --assert-max-length
```

---

## Function 270M

```shell
python dataset.py --task hf_function_set --file tool/user-profile.train.jsonl
python dataset.py --task hf_tool_schema --tool user --file tool/user.tools.hf.json
```

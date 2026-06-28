# Router Agent
Instructions to build and evaluate router models.

## Router 270M

```shell
rm -rf router-270m/
```

```shell
python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 1e-5 --files router/router.train.hf.json --model /gemma-3-270m-it --output-dir router-270m --eval-steps 50 --save-steps 1000
```

```shell
python evaluate.py --model router-270m --files router/router.train.hf.json --max-new-tokens 400 --verbose --errors-only --error-threshold 0.9
```

## Router 270M Q4

```shell
CUDA_VISIBLE_DEVICES=1 python instruction-tuning.py --epochs 2 --train-batch 2 --learning-rate 1e-5 --files router/router.train.hf.json --model /gemma-3-270m-it --output-dir router-270m-peft --peft QLoRA --bf16 --max-length 800 --assert-max-length --eval-steps 100 --save-steps 1000
python merge.py --base-model /gemma-3-270m-it --peft-model router-270m-peft --output-dir router-270m-Q4

CUDA_VISIBLE_DEVICES=1 python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 5e-5 --files router/router.train.hf.json --model /gemma-3-4b-it --output-dir router-4b-peft --peft QLoRA --bf16 --max-length 800 --assert-max-length --eval-steps 100 --save-steps 1000
```

## Router 1B

```shell
rm -rf router-1b/
```

```shell
python instruction-tuning.py --epochs 3 --train-batch 2 --learning-rate 5e-5 --files router/router.train.hf.json --model /gemma-3-1b-it --output-dir router-1b --peft LoRA --max-length 800 --assert-max-length --eval-steps 100 --save-steps 1000
```

```shell
python evaluate.py --model router-1b --files router/router.train.hf.json --max-new-tokens 400 --verbose --errors-only --error-threshold 0.9
```

## Router 4B

```shell
rm -rf router-4b/
rm -rf router-4b-peft/
```

```sh
python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 5e-5 --files router/router.train.hf.json --model /gemma-3-4b-it --output-dir router-4b-peft --peft QLoRA --bf16 --max-length 800 --assert-max-length --eval-steps 100 --save-steps 1000
```

```shell
python merge.py --base-model /gemma-3-4b-it --peft-model router-4b-peft/ --output-dir router-4b
```

```shell
python evaluate.py --model router-4b --files router/router.train.hf.json --max-new-tokens 400 --verbose --errors-only --error-threshold 0.9
```

Train on CUDA:1
```shell
CUDA_VISIBLE_DEVICES=1 python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 1e-5 --files router/router.train.hf.json --model /gemma-3-270m-it --output-dir router-270m --eval-steps 50 --save-steps 1000
CUDA_VISIBLE_DEVICES=1 python instruction-tuning.py --epochs 2 --train-batch 2 --learning-rate 1e-5 --files router/router.train.hf.json --model /gemma-3-270m-it --output-dir router-270m --eval-steps 100 --save-steps 1000
```
Parallel train on two GPUs
```shell
 torchrun --nproc-per-node=2 instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 1e-5 --files router/router.train.hf.json --model /gemma-3-270m-it --output-dir router-270m --eval-steps 50 --save-steps 1000
```

---

## Router 270M

```shell
python dataset.py --task hf_router_set --file router/router.train.jsonl
python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 1e-5 --files router/router.train.hf.json --model /gemma-3-270m-it --output-dir router-270m --eval-steps 100 --save-steps 1000 --max-length 400 --assert-max-length
python instruction-tuning.py --epochs 2 --train-batch 1 --learning-rate 8e-6 --files router/router.train.hf.json --model /gemma-3-270m-it --output-dir router-270m --eval-steps 100 --save-steps 1000 --max-length 200 --assert-max-length
```

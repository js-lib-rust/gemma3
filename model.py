import argparse
import os
import shutil

import util

parser = argparse.ArgumentParser()
parser.add_argument("--base-model", action="store")
parser.add_argument("--tuned-model", action="store")
parser.add_argument("--load", action="store_true")
parser.add_argument("--force", action="store_true")
args = parser.parse_args()

print(f"Use base model {args.base_model}")
print(f"Use tuned model {args.tuned_model}")
print(f"Use load {args.load}")
print(f"Use force {args.force}")

if args.load:
    base_model = util.get_model_path(args.base_model)
    tuned_model = args.tuned_model
    if os.path.exists(tuned_model):
        if not args.force:
            print(f"Tuned model {tuned_model} already loaded.")
            exit(1)
        shutil.rmtree(tuned_model)

    shutil.copytree(base_model, tuned_model)


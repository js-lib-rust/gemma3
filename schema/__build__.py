from transformers.utils import get_json_schema
import importlib
from pathlib import Path
import json
import time

start_total = time.perf_counter()
print("🚀 Starting build process...")

module_files = list(Path('.').glob('*.py'))
if not module_files:
    print("❌ No .py files found in the current directory.")
    exit(1)

total_functions = 0
total_write_duration = 0
for module_file in module_files:
    if module_file.name.startswith('__'):
        continue

    start_file = time.perf_counter()
    print()
    print(f"📄 Processing: {module_file.name}...", end="", flush=True)

    app = module_file.name.rstrip(".py")
    prefix = app.replace('-', '_')
    module = importlib.import_module('.' + app, 'schema')
    functions = [get_json_schema(getattr(module, function)) for function in dir(module) if function.startswith(prefix)]

    total_functions += len(functions)
    duration_ms = (time.perf_counter() - start_file) * 1000
    print(f" Done! ({len(functions)} functions in {duration_ms:.1f}ms)")

    file_path = f"../data/tool/{app}.tools.hf.json"
    print(f"💾 Write {len(functions)} function definitions to {file_path}")
    write_start = time.perf_counter()

    with open(file_path, 'w', encoding='UTF-8') as f:
        json.dump(functions, f, indent=2, ensure_ascii=False)

    total_write_duration += (time.perf_counter() - write_start) * 1000

if not total_functions:
    print("❌ No function definitions found in the current directory.")
    exit(1)
total_duration = (time.perf_counter() - start_total) * 1000
assert total_duration > 0

print("\n" + "=" * 35)
print("📊 PERFORMANCE REPORT")
print("=" * 35)
print(f"Total Functions:    {total_functions}")
print(f"Total Time:         {total_duration / 1000:.3f} s ({total_duration:.1f} ms)")
print(f"Average Throughput: {total_functions / (total_duration / 1000):.2f} functions/sec")
print(f"File Write Time:    {total_write_duration:.1f} ms")
print("=" * 35)

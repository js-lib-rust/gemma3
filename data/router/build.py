import json
import time
from pathlib import Path
from typing import Generator, List, Dict

# Constant for the system prompt to avoid repeated string creation
SYSTEM_PROMPT = {"role": "system", "content": "Route and rewrite the next user prompt"}


def stream_jsonl_to_hf(jsonl_file: Path) -> Generator[List[Dict[str, str]], None, None]:
    """
    A generator that reads a JSONL file line by line to save memory.
    Yields formatted chat turns for HuggingFace datasets.
    """
    with jsonl_file.open('r', encoding='UTF-8') as file:
        for line in file:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('/*'):
                continue

            try:
                sample = json.loads(line)

                # Using extend for faster list construction
                turns = [SYSTEM_PROMPT]
                for turn in sample:
                    turns.extend([
                        {"role": "user", "content": turn["user"]},
                        {"role": "model", "content": turn["model"]}
                    ])

                yield turns

            except (json.JSONDecodeError, KeyError) as e:
                print(f"  [!] Error skipping line in {jsonl_file.name}: {e}")


def build_router_dataset(output_filename: str = "router.train.hf.json"):
    """
    Finds all .jsonl files in the current directory and aggregates them.
    Includes performance timing in milliseconds.
    """
    start_total = time.perf_counter()
    print("🚀 Starting build process...")

    dataset: List[List[Dict[str, str]]] = []
    jsonl_files = list(Path('.').glob('*.train.jsonl'))

    if not jsonl_files:
        print("❌ No .jsonl files found in the current directory.")
        return

    for jsonl_file in jsonl_files:
        start_file = time.perf_counter()
        print(f"📄 Processing: {jsonl_file.name}...", end="", flush=True)

        # Track samples added
        count_before = len(dataset)
        dataset.extend(stream_jsonl_to_hf(jsonl_file))
        count_after = len(dataset)

        # Calculate duration in milliseconds
        duration_ms = (time.perf_counter() - start_file) * 1000
        new_samples = count_after - count_before

        # Using .1f for cleaner millisecond display (e.g., 12.5ms)
        print(f" Done! ({new_samples} samples in {duration_ms:.1f}ms)")

    # Write the final dataset
    print(f"💾 Writing {len(dataset)} samples to {output_filename}...")
    write_start = time.perf_counter()

    with open(output_filename, 'w', encoding='UTF-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    write_duration_ms = (time.perf_counter() - write_start) * 1000
    total_duration_ms = (time.perf_counter() - start_total) * 1000

    # Final Report
    print("\n" + "=" * 35)
    print("📊 PERFORMANCE REPORT")
    print("=" * 35)
    print(f"Total Samples:      {len(dataset)}")
    print(f"Total Time:         {total_duration_ms / 1000:.3f} s ({total_duration_ms:.1f} ms)")
    if total_duration_ms > 0:
        print(f"Avg Throughput:     {len(dataset) / (total_duration_ms / 1000):.2f} samples/sec")
    print(f"Write Time:         {write_duration_ms:.1f} ms")
    print("=" * 35)


if __name__ == "__main__":
    build_router_dataset()

import json
import os
import glob


def extract_data_from_jsonl(directory_path):
    """
    Scans a directory for .jsonl files and extracts:
    1. The 'goal' (the first line of the model response).
    2. The 'actions' (all subsequent lines in the model response).
    Ensures both goals and actions are unique per file.
    """
    # Structure: { "filename.jsonl": { "goals": set(), "actions": set() } }
    results = {}

    search_pattern = os.path.join(directory_path, "*.jsonl")
    jsonl_files = glob.glob(search_pattern)

    if not jsonl_files:
        print(f"No .jsonl files found in {directory_path}")
        return {}

    for file_path in jsonl_files:
        file_name = os.path.basename(file_path)

        # We store two separate sets for this specific file
        file_data = {
            "goals": set(),
            "actions": set()
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_number, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("/*"):
                        continue  # Skip comments

                    try:
                        data = json.loads(line)

                        if isinstance(data, list) and len(data) > 0:
                            entry = data[0]
                            model_response = entry.get("model", "")

                            # Split the response into individual lines
                            lines = [line.strip() for line in model_response.split('\n') if line.strip()]

                            if not lines:
                                continue

                            # --- 1. Process the FIRST line (The Goal) ---
                            first_line = lines[0]
                            if ":" in first_line:
                                goal_content = first_line.split(':', 1)[1].strip()
                                file_data["goals"].add(goal_content)
                            else:
                                print(f"⚠️ Warning: No colon in {file_name} (Line {line_number})")

                            # --- 2. Process all SUBSEQUENT lines (The Actions) ---
                            if len(lines) > 1:
                                # Everything from index 1 to the end is an action
                                actions = lines[1:]
                                for action in actions:
                                    file_data["actions"].add(action)

                    except json.JSONDecodeError:
                        print(f"❌ Error: Invalid JSON on line {line_number} in {file_name}")
                    except Exception as e:
                        print(f"❌ Error processing line {line_number} in {file_name}: {e}")

            # Only add to results if we actually found something in this file
            if file_data["goals"] or file_data["actions"]:
                results[file_name] = file_data

        except Exception as e:
            print(f"❌ Could not read file {file_name}: {e}")

    return results


def main():
    target_directory = "."
    extracted_data = extract_data_from_jsonl(target_directory)

    print("\n=== Extracted Goals & Actions per File ===\n")
    if not extracted_data:
        print("No data was found.")
    else:
        for filename, content in extracted_data.items():
            print(f"📄 FILE: {filename}")

            print("  🎯 GOALS:")
            if content["goals"]:
                for goal in sorted(list(content["goals"])):
                    print(f"     - {goal}")
            else:
                print("     (None)")

            print("  🛠️ ACTIONS:")
            if content["actions"]:
                for action in sorted(list(content["actions"])):
                    print(f"     - {action}")
            else:
                print("     (None)")

            print("-" * 40)


if __name__ == "__main__":
    main()

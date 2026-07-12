import json
import os
import glob


def extract_goals_from_jsonl(directory_path):
    """
    Scans a directory for .jsonl files and extracts the 'goal'
    from the first line of the model response in each entry.
    """
    # This dictionary will store: { "filename.jsonl": ["goal1", "goal2", ...] }
    results = {}

    # Find all files ending in .jsonl in the specified directory
    search_pattern = os.path.join(directory_path, "*.jsonl")
    jsonl_files = glob.glob(search_pattern)

    if not jsonl_files:
        print(f"No .jsonl files found in {directory_path}")
        return {}

    for file_path in jsonl_files:
        file_name = os.path.basename(file_path)
        goals = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_number, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue  # Skip empty lines
                    if line.startswith("/*"):
                        continue  # Skip comments

                    try:
                        # 1. Parse the JSON line
                        # Format: [{"user": "...", "model": "..."}]
                        data = json.loads(line)

                        # 2. Access the first element in the list
                        if isinstance(data, list) and len(data) > 0:
                            entry = data[0]
                            model_response = entry.get("model", "")

                            # 3. Split the multiline response by '\n'
                            lines = model_response.split('\n')

                            if lines:
                                first_line = lines[0].strip()

                                # 4. Check if the first line contains a colon
                                if ":" in first_line:
                                    # Extract everything after the first colon
                                    # Split(maxsplit=1) ensures we only split at the first colon
                                    goal_content = first_line.split(':', 1)[1].strip()
                                    goals.add(goal_content)
                                else:
                                    print(f"⚠️ Warning: No colon found in line 1 of {file_name} (Entry {line_number})")

                    except json.JSONDecodeError:
                        print(f"❌ Error: Invalid JSON on line {line_number} in {file_name}")
                    except Exception as e:
                        print(f"❌ Error processing line {line_number} in {file_name}: {e}")

            # Add the collected goals to our results dictionary
            if goals:
                results[file_name] = goals

        except Exception as e:
            print(f"❌ Could not read file {file_name}: {e}")

    return results


def main():
    # Set the directory containing your jsonl files here
    target_directory = "."

    # Create the directory and a dummy file for testing if it doesn't exist
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        print(f"Created {target_directory} for demonstration.")

    # Run extraction
    extracted_data = extract_goals_from_jsonl(target_directory)

    # Print the output
    print("\n=== Extracted Goals per File ===\n")
    if not extracted_data:
        print("No goals were found.")
    else:
        for filename, goals in extracted_data.items():
            print(f"📄 {filename}")
            for goal in goals:
                print(f"   - {goal}")
            print("-" * 30)


if __name__ == "__main__":
    main()

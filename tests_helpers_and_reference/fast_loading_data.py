import json

eval_set_path = "./transcript_evaluation_sets/relationship_transcript_evaluation_set.json"

# Load the verified dataset
with open(eval_set_path, "r", encoding="utf-8") as f:
    eval_set = json.load(f)

# Split into evaluation buckets
obvious_cases = [d for d in eval_set if "Obvious" in d["type"]]
ambiguous_cases = [d for d in eval_set if "Ambiguous" in d["type"]]

print(f"Loaded {len(eval_set)} dialogues successfully!")
print(f"Obvious: {len(obvious_cases)} | Ambiguous: {len(ambiguous_cases)}")

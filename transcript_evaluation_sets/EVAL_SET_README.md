# Dataset Overview

This evaluation set provides exactly 30 synthetic relationship conversations carefully curated to benchmark emotion, tone, and relationship status classification systems. The conversations are balanced to offer realistic baseline performance checks.

- Length: Each conversation contains exactly 6 turns (fitting the 4–8 turn requirement perfectly).

- Mix: 15 dialogues feature Obvious Scenarios (e.g., severe conflict, deep romance, overt contempt, validation, clear teamwork) and 15 feature Ambiguous Scenarios (e.g., hidden subtext, passive-aggressive tones, drift, unaligned future pacing, family boundaries).

## Format Availability

- .json: Best for directly ingestion into Python/Hugging Face evaluation loops.
- .csv: Formatted in flat rows (Dialogue ID, Category, Turn Number, Speaker, Text) for easy DataFrame analysis.
- .pdf: Cleanly styled document for manual qualitative review.

## Python Fastloading

```Python
import json

# Load the verified dataset
with open("relationship_transcript_evaluation_set.json", "r", encoding="utf-8") as f:
    eval_set = json.load(f)

# Split into evaluation buckets
obvious_cases = [d for d in eval_set if "Obvious" in d["type"]]
ambiguous_cases = [d for d in eval_set if "Ambiguous" in d["type"]]

print(f"Loaded {len(eval_set)} dialogues successfully!")
print(f"Obvious: {len(obvious_cases)} | Ambiguous: {len(ambiguous_cases)}")
```

# POC #1

A repo for an ML POC to analyze and classify conversational patterns.

## Directory layout

- `pipeline/` — the final working pipeline: `raw_transcript.txt` → `txt_to_json_transformer.py` → `multi_agent_cot_batch_analyzer.py` → `visualize_results.py` logic → `generate_dynamic_report.py`, documented end-to-end in `full_behavior_analysis_pipeline.ipynb`. Outputs land in `pipeline/full_behavior_analysis_pipeline/`.
- `experiments/` — earlier baseline/grounding/role-based/multi-agent experiment scripts (`old_models/`), their outputs (`old_model_analysis_results/`), and the resulting charts (`visualizations/`).
- `transcript_evaluation_sets/` — the static 30-sample evaluation set used to score the experiments.
- `reference/` — label definitions and helper scripts (`temporary_ontology.md`, `fast_loading_data.py`, `ollama_check.py`).

## POC

### 1. Define 4 labels, manually

2–3 sentence operational definition of each, with two positive and two negative examples:

- criticism
- defensiveness
- validation
- repair attempt

### 2. Create 20–50 tiny transcript samples

Synthetic data cannot validate the eventual scientific claim, but it can answer your immediate engineering question:

- Can a detector be constructed at all?

### 3. Instantiate the dumbest possible baseline

Establish whether the basic behavioral classification problem seems tractable. Using llama 3.2.

Input:

```Python
A: You never listen to anything I say.
B: That's ridiculous. I listen all the time.
A: You're doing it right now.
B: Because you're attacking me.
```

Expected output:

```Python
{
  "criticism": {
    "detected": true,
    "confidence": 0.86,
    "evidence": "You never listen to anything I say."
  },
  "defensiveness": {
    "detected": true,
    "confidence": 0.82,
    "evidence": "I listen all the time."
  },
  "validation": {
    "detected": false,
    "confidence": 0.91
  },
  "repair_attempt": {
    "detected": false,
    "confidence": 0.87
  }
}
```

Look at the generated JSON output in your terminal. To establish if the problem is tractable, check for two things:

- Evidence alignment: Did it successfully pull "You never listen to anything I say." for criticism?
- Schema compliance: Did the local model output perfect JSON without syntax errors?

### 4. Score it

Compare the model against the 30 labeled examples.

Calculate per-label:

```Python
precision
recall
F1
false positives
false negatives
```

### 5. Add grounding

Give the model explicit behavior definitions along with every classification request.

Compare:

Experiment A

- Transcript → LLM → labels

Experiment B

- Behavior definitions + transcript → LLM → labels

Static grounding is enough to test the underlying hypothesis:

```Python
Does supplying a precise therapeutic framework make the classification more faithful?
```

### 6. Add audio

1. Use an existing audio recorder to record a 2–3 minute mock disagreement.

2. Run it through a speech-to-text app (iPhone Voice Memos).

3. Parse the text into json.

4. Pass the test sample to the model.

*The core multi-agent-cot framework worked best on the tricky, unstructured live transcript sample. The basic validation engine is ready.

The pipeline:

```Python
audio
  ↓
transcript
  ↓
turn segmentation
  ↓
behavior classifier
  ↓
timestamps + detections
```

Future work needed for the final step, timestamps + detections.

### Output a report

Example:

```Python
SESSION LENGTH: 2:43

00:31
Possible criticism — HIGH
"You never take me seriously."

00:37
Possible defensiveness — MODERATE
"That's not true. I always listen to you."

01:12
Possible repair attempt — MODERATE
"Okay. Can we start this over?"

01:16
Validation — HIGH
"Yeah. I think we're both getting frustrated."


SUMMARY

Criticism             2
Defensiveness         3
Validation            2
Repair attempts       1
```

Then optionally let an LLM convert only those structured observations into:

“One pattern worth reviewing occurred around 00:31, when a specific disagreement shifted into a broader statement about the other person's behavior…”

## Additional resources

Refer to [these behavior definitions](reference/temporary_ontology.md).

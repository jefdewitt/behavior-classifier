# POC #2 — Behavior Classifier Evaluation

## Goal: Determine whether the four relationship behaviors can be classified reliably, and whether theory grounding and conversation context improve performance

### Phase 1 — Freeze the ontology

Our four labels stay:

- Criticism
- Defensiveness
- Validation
- Repair attempt

For each label, write and freeze:

- operational definition
- inclusion criteria
- exclusion criteria
- 2 clear positive examples
- 2 hard-negative examples

Deliverable: ontology.json

### Phase 2 — Define the synthetic test set

Create ~8–10 mundane relationship scenarios independently of labels:

chores, money, lateness, phones, parenting, plans, work stress, intimacy, family/in-laws, household responsibilities

Use three difficulty levels:

- obvious
- subtle
- hard-negative

Then create the matrix before generating anything.

For example:

| Target | Obvious | Subtle | Hard negative |
| ------ | ------- | ------ | ------------- |
| Criticism	| 4	| 4 | 	3 |
| Defensiveness	| 4	| 4	| 3 |
| Validation | 4 | 4	| 3 |
| Repair attempt	| 4	| 4	| 3 |

44 planned test cases.

Deliverable: generation_plan.json

### Phase 3 — Generate conversations

Generate 4–8 turn conversations, because our behaviors can depend on what happened immediately before them.

Each generated sample gets metadata such as:

{
  "id": "def_subtle_03",
  "scenario": "chores",
  "intended_label": "defensiveness",
  "difficulty": "subtle",
  "dialogue": [
    {"speaker": "A", "text": "..."},
    {"speaker": "B", "text": "..."}
  ]
}

Generation is constrained by the ontology from Phase 1.

Deliverable: poc2_generated.json

### Phase 4 — Human QC

Inspect every generated example.

Reject/regenerate examples where:

- the intended behavior isn't actually present
- multiple labels are hopelessly entangled
- dialogue sounds artificial
- label terminology leaks into the dialogue
- keywords make the answer trivial
- we can't clearly justify the gold label

Then assign the actual gold labels.

Important distinction:

generated/intended label ≠ automatically the gold label.

The human-reviewed label becomes truth.

Deliverable: poc2_gold.json

### Phase 5 — Experiment A: Baseline

Run the existing POC classifier unchanged against the frozen dataset.

Measure per label:

TP / FP / TN / FN → precision / recall / F1

Plus macro-F1.

Create an error table:

|Sample|Gold|Prediction|Error|Likely reason|
|------|----|----------|-----|-------------|
|07|defensiveness|none|FN|explanation interpreted as neutral|
|14|none|criticism|FP|negativity confused with criticism|

Deliverables: experiment_a.json + error analysis.

### Phase 6 — Experiment B: Theory grounding

Same frozen test set.

Change one thing:

Give the classifier our operational definitions, inclusion criteria, and exclusions.

Then compare:

Experiment A
classifier alone
      ↓
performance

        VS.

Experiment B
classifier + ontology
      ↓
performance

This answers:

Does explicit theory grounding improve behavioral classification?

### Phase 7 — Experiment C: Context

Again: same frozen examples.

For each target behavior test:

C1

target utterance only → classifier

C2

full conversation → classifier

Compare performance by label.

Hypothesis:

Context will matter disproportionately for defensiveness and repair attempts, because their meaning frequently depends on the preceding conversational move.

### Phase 8 — Decide what POC #3 should be

Only after A/B/C.

Depending on the results:

Definitions help
      ↓
Explore RAG / richer theory grounding

Context helps
      ↓
Explore contextual conversation models

Both help
      ↓
Combine them

Neither helps
      ↓
Revisit ontology / task formulation

Performance is already excellent
      ↓
Challenge it with harder real-world data

And fine-tuning XLM-R is not part of POC #2.

The DefMoN discovery tells us that XLM-R is a credible future supervised baseline.

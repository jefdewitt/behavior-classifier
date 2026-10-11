# POC #2 — Behavior Classifier Evaluation

## Goal: Determine whether the four relationship behaviors can be classified reliably, and whether theory grounding and conversation context improve performance

> **Status: Frozen (2026-10-11).** Gold dataset v1.2.1, ontology v1.0.0. Experiments A, B, C and the Opus capacity comparison are complete; their inputs, code and results are listed with SHA-256 hashes in `poc2_freeze_manifest.json`. Do not edit or re-run POC 2 artifacts; new work belongs in POC 3. See **Results** at the end of this file.

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
| Criticism | 4 | 4 | 3 |
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

Run the POC 1 multi-agent CoT approach as a POC 2 baseline against the frozen gold dataset. The POC 2 runner uses the full dialogue as context, marks the focal turn, and asks for predictions about that turn only. It does not provide the ontology; its prompts are generic and contain no POC 1 transcript-specific examples or verdicts.

Run from the repository root:

```sh
python poc2/multi_agent_cot_baseline.py
```

This writes `experiment_a.json` and `experiment_a_error_analysis.json` in `poc2/`. The result records the input hash, model, prompt version, target-turn scoring scope, metrics, predictions, and model-generated error notes. Review the error notes manually.

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

The runner adds these from `ontology.json` to the shared instructions given to all three agents. Examples are not included. Everything else is identical to Experiment A.

Run from the repository root:

```sh
python poc2/multi_agent_cot_baseline.py --experiment B
```

This writes `experiment_b.json` and `experiment_b_error_analysis.json` in `poc2/`.

#### B-alternate: model-capacity comparison

Same prompt, ontology content, dataset, output schema, and evaluation as Experiment B; only the model changes, from local `llama3.2` (Ollama) to hosted Claude Opus 5.5 (Anthropic API). Providers live in `poc2/llm_providers.py`. Put `ANTHROPIC_API_KEY=...` in a `.env` file at the repository root (git-ignored), then run:

```sh
python poc2/multi_agent_cot_baseline.py --experiment B --provider anthropic
```

This writes `experiment_b_claude-opus-5-5.json` and its error analysis. Sampling cannot be matched exactly: Claude Opus 5.5 does not accept temperature or seed, and its adaptive thinking cannot be disabled. The run uses a fixed effort level, recorded in `model_options`.

Compare runs with:

```sh
python poc2/visualize_experiments.py --input poc2/experiment_a.json --input poc2/experiment_b.json
```

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

### Phase 7 — Experiment C: Context Ablation

Again: same frozen examples.

Experiment C removes context to measure what context contributes. It is an ablation, not a competitor to B: C is expected to score at or below B, and the size of the drop by label is the result.

Start from Experiment B and change one thing: remove every turn except the focal turn.

Experiment B (reference)

full conversation, focal turn marked + ontology definitions and criteria → classifier

        VS.

Experiment C

focal turn only + ontology definitions and criteria → classifier

The prompt, ontology content, model, and scoring are identical to B. The focal turn is shown without its turn number, since "Turn 3" would itself reveal that earlier turns exist.

Run from the repository root:

```sh
python poc2/multi_agent_cot_baseline.py --experiment C
```

This writes `experiment_c.json` and `experiment_c_error_analysis.json` in `poc2/`.

Compare performance by label: B − C is the contribution of context.

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

## Results

All runs use the frozen gold set (`poc2_gold.json` v1.2.1, 44 samples: 8 positives and 3 hard negatives per label), the same three-agent pipeline, and llama3.2 at temperature 0, seed 42, unless noted. "Target F1" scores each sample's target label, as specified in Phase 5. "All-labels F1" scores all four labels on every focal turn against `target_turn_gold_labels`; it is stricter, because the target-label design favours "yes" (a classifier that always answers yes scores 0.84 target macro-F1).

| Run | Change | Target macro-F1 | All-labels macro-F1 | Trick examples correct | Results |
|---|---|---|---|---|---|
| A | Baseline: full dialogue, no ontology | 0.81 | 0.47 | 9/12 | `experiment_a.json` |
| B | A + ontology definitions and criteria | 0.92 | 0.50 | 9/12 | `experiment_b.json` |
| B, Opus | B with Claude Opus 5.5 instead of llama3.2 | 1.00 | 0.91 | 12/12 | `experiment_b_claude-opus-5-5.json` |
| C | B with context removed (focal turn only) | 0.93 | 0.57 | 11/12 | `experiment_c.json` |

Error reviews: `experiment_a_error_review.md`, `experiment_b_error_review.md`, `experiment_c_error_review.md`. Side-by-side reports: `experiment_ab_comparison.html` (A, B, B Opus) and `experiment_bc_comparison.html` (B, C). `experiment_a_comparison.html` is from an early, unseeded Experiment A run on gold v1.1.0 and is superseded.

### Experiment B: theory grounding

Theory grounding raised target macro-F1 from 0.81 to 0.92 on llama3.2, fixing 9 of A's 11 errors and introducing 3. The gain was entirely on positives (24 → 30 of 32); hard negatives were unchanged (9 of 12), and B answered "yes" to 57% of label decisions against a gold rate of 20%. On all-labels scoring the gain was small (0.47 → 0.50). Paired test of B vs A errors: p ≈ 0.15.

### Opus capacity comparison

Same prompt, ontology content, dataset and evaluation as B; only the model changed. Claude Opus 5.5 scored 44/44 on target labels and 0.91 all-labels macro-F1, with a "yes" rate of 24% and no inexact evidence quotes. The initial research question holds: with theory grounding and a capable model, the four behaviors were reliably classifiable on this dataset. Llama3.2's over-labeling, criterion echoing and focal-turn attribution errors are limitations of the 3B model, not of the task. Caveats: Opus does not accept temperature or seed and always reasons before answering (effort fixed at high), and the dataset is now at ceiling for a frontier model. Llama3.2 remains the development model; Opus is used selectively to separate design limitations from model-capacity limitations.

### Experiment C: context ablation

Removing context did not lower overall performance on llama3.2 (target macro-F1 0.92 → 0.93; all-labels 0.50 → 0.57). Two effects offset each other:

- **Context supplied meaning.** Defensiveness dropped (1.00 → 0.86), and C missed val_subtle_03, whose validation depends on the partner's preceding disclosure.
- **Context distracted the 3B model.** C fixed three of B's focal-turn attribution failures, where llama reasoned about a following turn instead of the focal turn; inexact evidence quotes fell from 6 to 0.

C's four errors: three classification failures (two identifiable from the focal turn alone) and one ontology-boundary issue (cri_hn_03, also wrong in B). See `experiment_c_error_review.md`.

### Context-dependency hypothesis

The Phase 7 hypothesis (context matters disproportionately for defensiveness and repair attempts) is supported only where the focal turn is ambiguous on its own. Most POC 2 focal turns carry lexical cues that identify their label without context ("You never…", "I'm sorry…", "Of course you're anxious…"), so this dataset can show context's contribution on only a few samples.

Refined hypothesis for POC 3: **when a focal utterance is held constant, its correct label changes with the preceding dialogue, and a classifier that reads context recovers those changes while a focal-only classifier cannot.** Testing it requires a controlled dataset in which context, not lexical content, determines the correct interpretation.

### Phase 8 decision

POC #3 tests whether the task genuinely requires multi-turn reasoning, using context-dependent minimal pairs. See `poc3/poc3_instructions_README.md`. The architecture stays as is.


# POC #3 — Context-Dependent Minimal Pairs

## Goal: Determine whether the task genuinely requires multi-turn reasoning: does preceding context change the correct interpretation of an utterance, and does the classifier recover that change?

### Why

POC #2 (frozen; see `poc2/poc2_instructions_README.md` → Results) showed that the four behaviors are classifiable on its synthetic dataset. Claude Opus 5.5 scored 44/44 with theory grounding. But its context ablation (Experiment C) could not show what context contributes. Most focal turns carried lexical cues that identify their label on their own ("You never…", "I'm sorry…", "Of course you're anxious…"), so removing context barely mattered.

POC #3 is therefore a controlled test, not a harder dataset. It holds the focal utterance constant and changes only the preceding dialogue. If context matters, the correct label changes while the words do not.

### Hypotheses

- **H1 (task):** For a fixed focal utterance, the correct label depends on the preceding dialogue. Human QC must confirm this for every set before any model is run.
- **H2 (classifier):** With context, the classifier assigns different labels across a set's variants, matching the gold changes more often than a focal-only classifier can.
- **H3 (labels):** Context dependency is greatest for defensiveness and repair attempts, because both are defined as responses to a preceding move.

### Scope

In scope: a new dataset, a context condition, a focal-only condition, and set-level scoring.

Out of scope: new architecture, new agents or prompts, fine-tuning, and real-world data. The POC #2 pipeline (`multi_agent_cot_baseline.py`, Experiment B configuration with ontology definitions and criteria) is reused as is.

### Model policy

- **Development model:** llama3.2 via Ollama (local, no cost), temperature 0, seed 42.
- **Opus, selectively:** Claude Opus 5.5 is used only to tell a design limitation from a 3B-model limitation, for example when llama fails a set and it is unclear whether the set is flawed or the model is too weak. Each Opus run is approved before it starts.

## Dataset design

### Minimal-pair set

A set is one focal utterance placed after two or more different preceding dialogues:

- the focal utterance is **identical** across variants, word for word, spoken by the same speaker
- only the **preceding** turns change
- the focal turn is the **last** turn, with nothing after it. In POC #2 the following turn often revealed the label (for example "That's not an apology"), and llama misattributed following turns to the focal turn
- each variant has a full gold label vector (all four labels), and at least two variants in a set have different vectors

### Choosing focal utterances

A candidate focal utterance is kept only if both conditions hold:

1. **It is ambiguous alone.** Read without context, it does not clearly meet any label's criteria. This avoids the POC #2 problem of lexically marked turns.
2. **Its alternative readings are ontology-valid.** For each variant, the designer names the specific inclusion criterion the focal turn meets in that context, or the exclusion that keeps it out. A reading that is intuitive but fits no criterion does not count.

Rule 2 matters. Short concessions are attractive probes, but the ontology often excludes them. For example, "Okay, I'll do it" after an escalating argument likely falls under repair's exclusions for appeasement and practical-only solutions, and compliance meets no defensiveness criterion. It may therefore be "none" in every context. Finding that out during design is a result in itself, and it either drops the candidate or flags an ontology boundary for review.

### Worked example (to be validated in QC)

Focal utterance (Speaker B): **"I was going to do it after dinner."**

| Variant | Preceding dialogue | Gold | Criterion |
| --- | --- | --- | --- |
| 1 | A: Are you doing the dishes tonight, or should I? | none | Information only; no complaint to respond to |
| 2 | A: The dishes are still in the sink. You said you'd handle them, and once again it's fallen to me. | defensiveness | "Offers an excuse primarily to dismiss accountability rather than to add context while acknowledging impact" |

Variant 2 is only defensive because it answers a complaint without acknowledging its impact. The same words after a neutral question are not.

### Context-invariant controls

To check that the classifier does not overweight context, include control sets whose focal utterance is lexically marked ("You never think about anyone but yourself"), so its label should **not** change across contexts. A classifier should keep these stable.

### Size and balance

- Target about 16 minimal-pair sets × 2–3 variants plus about 8 control sets × 2 variants, giving roughly 60 items.
- Balance positives and negatives per label. POC #2's 8:3 ratio let an always-yes classifier score 0.84 target macro-F1.
- Spread sets across the four labels, with more for defensiveness and repair attempts (H3).

### Structure rules (from POC #2)

- Strict A/B alternation; no consecutive same-speaker turns.
- Vary the focal speaker (A or B) and focal position (Turn 2 to Turn 6) across sets, keeping both fixed within a set.
- Vary turn length, including multi-sentence turns.
- Check speaker-role coherence in every variant: each turn must make sense from its labeled speaker. POC #2 needed 15 such fixes after generation (gold v1.2.0 and v1.2.1).

### Proposed sample schema

```json
{
  "set_id": "S07",
  "set_type": "minimal_pair",
  "variant_id": "S07-v2",
  "focal_utterance": "I was going to do it after dinner.",
  "dialogue": [
    {"speaker": "A", "text": "The dishes are still in the sink. You said you'd handle them, and once again it's fallen to me."},
    {"speaker": "B", "text": "I was going to do it after dinner."}
  ],
  "target_turn_index": 1,
  "gold_labels": ["defensiveness"],
  "gold_rationale": {"defensiveness": "Offers an excuse primarily to dismiss accountability rather than to add context while acknowledging impact."},
  "focal_only_qc": "ambiguous"
}
```

`set_type` is `minimal_pair` or `control`.

## Phases

### Phase 1 — Confirm the ontology

Reuse ontology v1.0.0 unless design surfaces a boundary problem. POC #2 flagged one candidate: whether naming a recurring behavior ("left for me again") is an enduring-pattern criticism (`poc2/experiment_c_error_review.md`, cri_hn_03). Any change is versioned (v1.1.0) and frozen before generation.

### Phase 2 — Design the sets

Select focal utterances and write each variant's intended label with its named criterion, before generating dialogue.

### Phase 3 — Generate the preceding dialogues

Generate only the preceding turns for each variant, holding the focal utterance fixed.

### Phase 4 — Human QC

For every set:

1. **Focal-only read:** without seeing context, can the label be determined? It must not be, for minimal-pair sets.
2. **In-context read:** with context, is each variant's label clear and criterion-backed?
3. **Coherence:** each turn makes sense from its labeled speaker.

Drop or revise sets that fail. Record disagreements. Freeze the dataset with a version and hash.

### Phase 5 — Run the experiments

Same model, prompt and ontology content in every condition (llama3.2, Experiment B configuration):

- **Context:** preceding dialogue + focal turn.
- **Focal-only:** focal turn alone (POC #2 Experiment C mode). Because the focal utterance is identical across a set's variants, this condition must give the same prediction for every variant. That fixes an upper bound on its set-level score.

### Phase 6 — Score

- **Item level:** all-labels F1 per label, the primary metric, plus target-label F1 for continuity with POC #2.
- **Set level:** share of minimal-pair sets where every variant is correct.
- **Context sensitivity:** share of minimal-pair sets where the prediction changes across variants in the direction of the gold change.
- **Invariance:** share of control sets where the prediction stays the same.
- **Context contribution:** context minus focal-only, by label (H3).

This needs set-level scoring added to the evaluation; the classifier pipeline does not change.

### Phase 7 — Decide what comes next

- **Context changes the correct label, and the classifier follows:** the task needs multi-turn reasoning and the pipeline handles it. Move to harder or real-world data.
- **Context changes the label, but llama does not follow and Opus does:** a model-capacity limit. Decide when to adopt a foundation model.
- **Neither follows:** revisit how context is presented to the classifier.
- **Few candidate utterances survive QC:** for this ontology, context changes interpretation less often than assumed. That is a finding about the task and the ontology.

## Backlog carried forward from POC #2

- **Pipeline reliability (llama3.2).** About half of Experiment A's errors were output failures: empty or bare "Negative"/"Positive" notes, and notes contradicting the predicted value. See `poc2/experiment_a_error_review.md`.
- **Focal-turn attribution.** Llama reasoned about following turns instead of the focal turn (three of Experiment B's five errors). POC #3 removes following turns by design.
- **Sample size and run-to-run noise.** With 11 samples per label, one flipped prediction moves F1 by about 0.1, and per-label F1 moved by up to 0.04 between runs. Prefer more items per label and repeated runs.
- **Gold label completeness.** Opus predicted 7 labels not listed in the gold set, most of them defensible (for example, repair attempt on turns that take responsibility). POC #3 gold should list every label a variant meets, not only the intended one.
- **Supervised baseline.** Fine-tuning XLM-R is out of scope; DefMoN suggests it is a credible future baseline.

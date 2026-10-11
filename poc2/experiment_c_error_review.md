# Experiment C (Context Ablation) — error review

Source: `experiment_c.json` (created 2026-10-11T00:02:12.357909+00:00, gold v1.2.1, model llama3.2, options {'temperature': 0, 'seed': 42}, input mode `focal_turn_only`, input sha256 `f34049a1ae5d…`).

Each error is classified as one of:

- **Classification failure**: the information needed is available to the classifier, and it applies the label wrongly.
- **Ontology-boundary issue**: the definitions and criteria do not clearly decide the case.
- **Focal-turn attribution failure**: the classifier bases the decision on a turn other than the focal turn.

**Needs context?** records whether the label can be determined from the focal turn alone. The gold set was not modified based on these predictions. Entries marked **[Claude draft]** were written by Claude, not by a human reviewer.

## Summary

|Sample|Gold|C prediction|Error|In B?|Category|Needs context?|
|------|----|------------|-----|-----|--------|--------------|
|cri_hn_03|not criticism|criticism|FP|yes|Ontology-boundary issue|No (lexically marked)|
|def_obvious_02|defensiveness|not defensiveness|FN|no|Classification failure|Partly|
|def_subtle_01|defensiveness|not defensiveness|FN|no|Classification failure|Partly|
|val_subtle_03|validation|not validation|FN|no|Classification failure|Yes|

## Cross-cutting findings _[Claude draft]_

- **No focal-turn attribution failures.** With only the focal turn shown, there is no other turn to misattribute. Three of B's five errors were attribution failures (val_hn_01, rep_hn_03, rep_subtle_04), and all three are correct in C. Context gave llama 3B material to confuse with the focal turn.
- **Three classification failures, one ontology-boundary issue.** Two of the classification failures (def_obvious_02, def_subtle_01) are identifiable from the focal turn alone; llama simply misapplied the label, and with degenerate notes in def_subtle_01. Only val_subtle_03 genuinely depends on the preceding turn.
- **The ontology-boundary issue predates the ablation.** cri_hn_03 is wrong in B too; it reflects the recurring-behavior vs enduring-pattern boundary, which a capable model (Opus) resolved but llama did not.
- **Implication for the context hypothesis.** Most POC 2 focal turns carry lexical cues that identify the label without context, so this dataset can show context's value on only a few samples. That motivates POC 3's minimal-pair design.

---

## cri_hn_03 — FP

- **Target label:** criticism (hard_negative)
- **Gold:** 0  ·  **C (no context):** 1  ·  **B (llama, context):** 1  ·  **B (Opus, context):** 0
- **Gold labels on focal turn:** none
- **Ontology criterion (exclusion):** A specific complaint that identifies an observable behavior, its impact, or a requested change without attacking character.

**Full dialogue (C saw only the focal turn):**

> Turn 1 | A: The recycling is still by the door.
>
> Turn 2 | B: I forgot it this morning.
>
> **Turn 3 | A: I'm angry that the recycling was left for me again. Please take it out before dinner.  ← FOCAL**
>
> Turn 4 | B: I will do it now.

**Model note:** Yes

**Model evidence:** Please take it out before dinner

**Other labels (C):** defensiveness no (0.8), validation yes (0.9), repair_attempt yes (0.9)

**Category:** _[Claude draft]_ Ontology-boundary issue

**Needs context?:** _[Claude draft]_ No (lexically marked)

**Likely reason:** _[Claude draft]_ The ontology's definition of criticism includes problems located in an "enduring pattern", while its exclusion covers "a specific complaint that identifies an observable behavior… or a requested change". A complaint about a recurring behavior ("left for me again") sits on that boundary, and only the withheld hard-negative example ("I'm angry that the dishes were left for me again…") resolves it. Llama made the same error with context (B), so it is not caused by the ablation. Opus classified it correctly from the same definitions. The notes are bare "Yes"/"No", so llama's reasoning is not visible.

**Gold label OK?:** _[Claude draft]_ Yes. Candidate ontology clarification for POC 3: state explicitly that naming a recurring behavior is not by itself an enduring-pattern judgment.

---

## def_obvious_02 — FN

- **Target label:** defensiveness (obvious)
- **Gold:** 1  ·  **C (no context):** 0  ·  **B (llama, context):** 1  ·  **B (Opus, context):** 1
- **Gold labels on focal turn:** defensiveness, criticism
- **Ontology criterion (inclusion):** Responds to a complaint with a counter-complaint or redirects blame to the other person.

**Full dialogue (C saw only the focal turn):**

> Turn 1 | A: Sorry, my meeting ran over.
>
> Turn 2 | B: I waited forty minutes without hearing from you.
>
> **Turn 3 | A: If you weren't so rigid about time, this wouldn't even be a problem.  ← FOCAL**
>
> Turn 4 | B: Wanting a message isn't being rigid.

**Model note:** does not deny or minimize responsibility, offer an excuse to dismiss accountability, respond with a counter-complaint, or adopt an innocent-victim stance.

**Model evidence:** If you weren't so rigid about time, this wouldn't even be a problem.

**Other labels (C):** criticism yes (0.9), validation no (0.7), repair_attempt no (0.6)

**Category:** _[Claude draft]_ Classification failure

**Needs context?:** _[Claude draft]_ Partly

**Likely reason:** _[Claude draft]_ The counter-blame is visible in the focal turn alone ("If you weren't so rigid about time, this wouldn't even be a problem" redirects the problem to the partner), and llama even marked it criticism for the character attack. Its defensiveness note says the turn does not "respond with a counter-complaint", which contradicts the turn. Context strengthens the reading (it shows this answers "I waited forty minutes"), but the label is identifiable without it. B (llama, with context) and Opus were both correct.

**Gold label OK?:** _[Claude draft]_ Yes. The gold also lists criticism on this turn, which C detected.

---

## def_subtle_01 — FN

- **Target label:** defensiveness (subtle)
- **Gold:** 1  ·  **C (no context):** 0  ·  **B (llama, context):** 1  ·  **B (Opus, context):** 1
- **Gold labels on focal turn:** defensiveness
- **Ontology criterion (inclusion):** Adopts an innocent-victim stance implying that the speaker did nothing wrong and is being unfairly attacked.

**Full dialogue (C saw only the focal turn):**

> Turn 1 | A: I felt ignored when you kept checking your phone while I was talking.
>
> Turn 2 | B: I was following the game score.
>
> Turn 3 | A: I was trying to tell you something important, and you kept looking away.
>
> **Turn 4 | B: I guess I'm not allowed to unwind for five minutes without it becoming a whole thing.  ← FOCAL**

**Model note:** No

**Model evidence:** _(none)_

**Other labels (C):** criticism no (0.0), validation yes (0.9), repair_attempt yes (0.9)

**Category:** _[Claude draft]_ Classification failure

**Needs context?:** _[Claude draft]_ Partly

**Likely reason:** _[Claude draft]_ Degenerate output: every note is a bare "Yes"/"No", defensiveness is false at confidence 0.0, and it marked validation and repair_attempt true at 0.9, which the turn does not support. The innocent-victim stance is marked by sarcasm in the turn itself ("I guess I'm not allowed to unwind… without it becoming a whole thing"); context confirms it is a reply to a complaint but is not required to see it. A had the same degenerate failure on this sample; B (with context) and Opus were correct.

**Gold label OK?:** _[Claude draft]_ Yes

---

## val_subtle_03 — FN

- **Target label:** validation (subtle)
- **Gold:** 1  ·  **C (no context):** 0  ·  **B (llama, context):** 1  ·  **B (Opus, context):** 1
- **Gold labels on focal turn:** validation
- **Ontology criterion (inclusion):** Shows understanding of the impact an event had on the other person.

**Full dialogue (C saw only the focal turn):**

> Turn 1 | A: I thought adding people to Saturday would make the weekend more fun.
>
> Turn 2 | B: I was disappointed. I had been counting on two quiet days with you.
>
> **Turn 3 | A: You had already spent the week counting on that downtime, and I changed what you thought you were coming home to.  ← FOCAL**
>
> Turn 4 | B: Yes. That is what got to me.

**Model note:** No

**Model evidence:** You had already spent the week counting on that downtime, and I changed what you thought you were coming home to.

**Other labels (C):** criticism yes (0.9), defensiveness yes (0.9), repair_attempt no (0.8)

**Category:** _[Claude draft]_ Classification failure

**Needs context?:** _[Claude draft]_ Yes

**Likely reason:** _[Claude draft]_ Stance inversion: the speaker owns the impact of their own change ("I changed what you thought you were coming home to"), but llama labeled it criticism (0.9) and defensiveness (0.9). A made the same inversion with context. This is the most context-dependent of the four: without B's preceding "I was disappointed… counting on two quiet days", the turn reads less clearly as reflecting the partner's emotion. Context gave llama what it needed in B; Opus was correct with context.

**Gold label OK?:** _[Claude draft]_ Yes

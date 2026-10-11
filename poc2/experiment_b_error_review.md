# Experiment B — error review

Source: `experiment_b.json` (created 2026-10-07T03:03:48.354744+00:00, gold v1.2.1, model llama3.2, options {'temperature': 0, 'seed': 42}, ontology definitions_and_criteria v1.0.0, input sha256 `f34049a1ae5d…`).

For each error, confirm or edit **Likely reason**, and use **Gold label OK?** to flag gold labels that look wrong. Entries marked **[Claude draft]** were written by Claude, not by a human reviewer.

## Summary

|Sample|Gold|Prediction|Error|In A?|Likely reason|
|------|----|----------|-----|-----|-------------|
|cri_hn_03|not criticism|criticism|FP|no (new)|Criterion echo; specific complaint read as character attack|
|val_obvious_03|validation|not validation|FN|no (new)|Label inversion: validation read as criticism/defensiveness|
|val_hn_01|not validation|validation|FP|no (new)|Off-focal evidence (Turn 4); problem-solving exclusion not applied|
|rep_subtle_04|repair_attempt|not repair_attempt|FN|yes|Narrow reading of repair; goodwill criterion ignored|
|rep_hn_03|not repair_attempt|repair_attempt|FP|yes|Off-focal evidence (Turn 4); practical-solution exclusion not applied|

A errors fixed by B: cri_obvious_03, cri_subtle_01, def_obvious_01, def_subtle_01, rep_hn_02, val_hn_02, val_subtle_01, val_subtle_03, val_subtle_04.

## Cross-cutting findings _[Claude draft]_

- **Over-labeling.** B answers "yes" to 57% of all label decisions (A: 49%), while only 20% of gold labels are positive. B often marks a turn as criticism and defensiveness together with its target label (val_obvious_03, rep_subtle_04).
- **Criterion echo.** Many B notes restate a criterion's wording instead of tying it to the turn. The criteria gave the model vocabulary, but not always the judgement to apply it.
- **Off-focal evidence persists.** Two of the five errors (val_hn_01, rep_hn_03) reason about Turn 4, and inexact evidence quotes rose from 1 (A) to 6 (B).
- **Interpretation of the headline gain.** Each label has 8 positives and 3 hard negatives, so a classifier that always says "yes" scores F1 0.84 per label (macro 0.84). A (0.81) is below that; B (0.92) is above it. B's improvement is entirely on positives (24 → 30 of 32 correct); on hard negatives it is unchanged (9 of 12 in both). Scoring all four labels on every focal turn against `target_turn_gold_labels` gives macro-F1 0.47 (A) vs 0.50 (B), with precision 0.24–0.40 in both. Caveat: gold lists only deliberately instantiated labels, so some of those false positives may be defensible.

---

## cri_hn_03 — FP (new in B)

- **Target label:** criticism (hard_negative)
- **Gold:** 0  ·  **B prediction:** 1  ·  **A prediction:** 0
- **Gold labels on focal turn:** none
- **Ontology criterion (exclusion):** A specific complaint that identifies an observable behavior, its impact, or a requested change without attacking character.

**Dialogue:**

> Turn 1 | A: The recycling is still by the door.
>
> Turn 2 | B: I forgot it this morning.
>
> **Turn 3 | A: I'm angry that the recycling was left for me again. Please take it out before dinner.  ← FOCAL**
>
> Turn 4 | B: I will do it now.

**Model note:** Attributes a problem to the other person's character, motives, or stable disposition.

**Model evidence:** I'm angry that the recycling was left for me again. Please take it out before dinner.

**Other labels (B):** defensiveness no (0.9), validation yes (0.7), repair_attempt yes (0.9)

**Likely reason:** _[Claude draft]_ Criterion echo: the note restates the inclusion criterion verbatim ("Attributes a problem to… stable disposition") without saying how the turn meets it. "Again" was likely read as a stable pattern, while the exclusion for a specific complaint with a requested change ("Please take it out before dinner") was not applied. The ontology's withheld hard-negative example is nearly identical ("I'm angry that the dishes were left for me again…"). New in B; A got this right.

**Gold label OK?:** _[Claude draft]_ Yes

---

## val_obvious_03 — FN (new in B)

- **Target label:** validation (obvious)
- **Gold:** 1  ·  **B prediction:** 0  ·  **A prediction:** 1
- **Gold labels on focal turn:** validation
- **Ontology criterion (inclusion):** Communicates that the reaction makes sense given the person's experience or the available context.

**Dialogue:**

> Turn 1 | A: Your manager moved the deadline up again?
>
> Turn 2 | B: Yeah. I planned around Friday, and now I'm panicking because two days of work got dumped into tonight.
>
> **Turn 3 | A: Of course you're anxious. You planned around Friday, and now two days of work got dumped into one night.  ← FOCAL**
>
> Turn 4 | B: Exactly.

**Model note:** Does not accurately name, reflect, or summarize Speaker B's emotion or perspective, nor does it show understanding of the impact an event had on Speaker B.

**Model evidence:** _(none)_

**Other labels (B):** criticism yes (0.9), defensiveness yes (0.9), repair_attempt no (0.0)

**Likely reason:** _[Claude draft]_ Label inversion: a textbook validation ("Of course you're anxious…") was marked criticism (0.9) and defensiveness (0.9), with notes that echo those labels' criteria, and validation false at 0.0. This is not a definitional gap; the turn meets the validation criteria plainly. The added criteria seem to have produced criterion-matching without reading the turn. New in B; A got this right.

**Gold label OK?:** _[Claude draft]_ Yes

---

## val_hn_01 — FP (new in B)

- **Target label:** validation (hard_negative)
- **Gold:** 0  ·  **B prediction:** 1  ·  **A prediction:** 0
- **Gold labels on focal turn:** none
- **Ontology criterion (exclusion):** Problem-solving or advice that bypasses acknowledgment of the emotion or perspective.

**Dialogue:**

> Turn 1 | A: Sorry, my phone died on the train.
>
> Turn 2 | B: I was worried when you were late and didn't text.
>
> **Turn 3 | A: I should keep a charger in my bag so this doesn't happen again.  ← FOCAL**
>
> Turn 4 | B: That would help, but I wanted you to understand why I was upset.

**Model note:** The phrase 'but I wanted you to understand' might suggest that Speaker B is seeking validation or reassurance rather than simply acknowledging their experience.

**Model evidence:** That would help, but I wanted you to understand why I was upset. _(not an exact quote)_

**Other labels (B):** criticism yes (0.8), defensiveness no (0.9), repair_attempt yes (0.9)

**Likely reason:** _[Claude draft]_ Off-focal evidence: the validation decision is about B's Turn 4 ("I wanted you to understand why I was upset"), and the note itself discusses Speaker B. The exclusion for problem-solving that bypasses acknowledgment, which fits the focal turn exactly, was not applied. It also marked criticism on "so this doesn't happen again". New in B.

**Gold label OK?:** _[Claude draft]_ Yes

---

## rep_subtle_04 — FN

- **Target label:** repair_attempt (subtle)
- **Gold:** 1  ·  **B prediction:** 0  ·  **A prediction:** 0
- **Gold labels on focal turn:** repair_attempt
- **Ontology criterion (inclusion):** Expresses care, shared purpose, or goodwill during conflict to reduce hostility and preserve connection.

**Dialogue:**

> Turn 1 | A: I should not have to manage you too.
>
> Turn 2 | B: And I should not have to guess what you want.
>
> **Turn 3 | A: I don't want this to become another round of who carries more. What did you need from me tonight?  ← FOCAL**
>
> Turn 4 | B: I needed you to take the laundry without waiting for me to ask.

**Model note:** The speaker does not take responsibility, apologize, or explicitly ask to pause and restart the conversation, but rather expresses a desire to avoid a specific situation.

**Model evidence:** I don't want this to become another round of who carries more.

**Other labels (B):** criticism yes (0.8), defensiveness yes (0.8), validation no (0.2)

**Likely reason:** _[Claude draft]_ Narrow reading of repair: the note checks only for taking responsibility, apologising or asking to restart, and ignores the criterion the gold cites (care, shared purpose or goodwill to reduce hostility). It marked the same sentence as criticism and defensiveness. Also an error in A, where it was a note/prediction mismatch.

**Gold label OK?:** _[Claude draft]_ Yes

---

## rep_hn_03 — FP

- **Target label:** repair_attempt (hard_negative)
- **Gold:** 0  ·  **B prediction:** 1  ·  **A prediction:** 1
- **Gold labels on focal turn:** none
- **Ontology criterion (exclusion):** A solution proposal that addresses only the practical problem without attempting to repair the interaction.

**Dialogue:**

> Turn 1 | A: We're going in circles about Saturday.
>
> Turn 2 | B: Because you won't compromise.
>
> **Turn 3 | A: I'll book the six o'clock reservation.  ← FOCAL**
>
> Turn 4 | B: That settles dinner, but we're still speaking to each other like enemies.

**Model note:** Positive. Speaker B's response is a repair attempt, as it seeks to address the interactional rupture caused by Speaker A's initial criticism. The phrase 'that settles dinner' is a softer way of saying 'I'm willing to move forward,' and the acknowledgment of the need to improve their communication is a step towards constructive engagement.

**Model evidence:** that settles dinner _(not an exact quote)_

**Other labels (B):** criticism yes (0.8), defensiveness no (0.9), validation yes (0.7)

**Likely reason:** _[Claude draft]_ Off-focal evidence: the repair and validation notes reason about B's Turn 4 ("that settles dinner", "speaking to each other like enemies"), and criticism attributes Turn 4's words to Speaker A. The practical-solution exclusion was not applied to the focal turn. Same error as A.

**Gold label OK?:** _[Claude draft]_ Yes

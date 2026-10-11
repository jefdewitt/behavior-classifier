# Experiment A — error review

Source: `experiment_a.json` (created 2026-10-07T02:20:07.709424+00:00, gold v1.2.1, model llama3.2, options {'temperature': 0, 'seed': 42}, input sha256 `f34049a1ae5d…`).

For each error, fill in **Likely reason** with your own judgement. Use **Gold label OK?** to flag cases where the gold label itself looks wrong (`yes`, or `no — <why>`).

## Summary

|Sample|Gold|Prediction|Error|Likely reason|
|------|----|----------|-----|-------------|
|cri_obvious_03|criticism|not criticism|FN|No rationale; likely read as a bounded complaint, not a global judgment|
|cri_subtle_01|criticism|not criticism|FN|Note/prediction mismatch|
|def_obvious_01|defensiveness|not defensiveness|FN|Degenerate output (bare Negative/Positive)|
|def_subtle_01|defensiveness|not defensiveness|FN|Degenerate output (all false, conf 0.0)|
|val_subtle_01|validation|not validation|FN|Paraphrase/reflection not recognised as validation|
|val_subtle_03|validation|not validation|FN|Owning the impact misread as criticism/defensiveness|
|val_subtle_04|validation|not validation|FN|Degenerate output (empty notes); validation without explicit markers|
|val_hn_02|not validation|validation|FP|Reassurance confused with validation|
|rep_subtle_04|repair_attempt|not repair_attempt|FN|Note/prediction mismatch|
|rep_hn_02|not repair_attempt|repair_attempt|FP|"I'm sorry" keyword; conditional apology not excluded|
|rep_hn_03|not repair_attempt|repair_attempt|FP|Practical solution confused with repair|

_def_subtle_02 was an error in the run on gold v1.1.0 and is correct on v1.2.0 (speaker-role fix); its section is kept below for the record._

_Dialogues below are from gold v1.2.1. Model notes and predictions are from the run on the gold version named in Source._

_Entries marked **[Claude draft]** were written by Claude, not by a human reviewer; confirm or edit them. cri_obvious_03 and cri_subtle_01 are the user's._

## Cross-cutting findings _[Claude draft]_

**Error types (11 errors on gold v1.2.0):**
- **Pipeline failures (5):** degenerate output (3: def_obvious_01, def_subtle_01, val_subtle_04) and note/prediction mismatch (2: cri_subtle_01, rep_subtle_04). These are about how the model fills in its answer, not how it understands the labels, so giving it the ontology (Experiment B) may not fix them.
- **Conceptual confusions (6):** reassurance as validation (val_hn_02), conditional apology as repair (rep_hn_02), practical solution as repair (rep_hn_03), reflection not seen as validation (val_subtle_01), owning the impact misread as criticism (val_subtle_03), and a bounded complaint vs a global judgment (cri_obvious_03). Three of these match an ontology exclusion criterion word for word, so these are what Experiment B should fix if theory grounding helps.
- **Evidence from outside the focal turn:** in val_hn_02, rep_subtle_04 and rep_hn_03 (and rep_hn_02 for criticism, quoting Turn 2), the model quoted the next turn (B's Turn 4) as evidence for a label on the focal turn.

**Gold dataset issue: inconsistent speaker labels (fixed in gold v1.2.0 and v1.2.1).** Every dialogue is labeled strictly A/B/A/B, but in 15 of the 44 samples the text has the accused partner speaking in both Turn 2 and Turn 3, so the person who raised the complaint appears to defend against it. This tends to happen where the focal behavior is the accused partner's response but sits in Turn 3, which strict alternation gives to Speaker A. def_obvious_01 and rep_subtle_04 were first flagged but read coherently on a second look. Affected samples (confirmed; val_hn_02 added in v1.2.1): def_obvious_02, def_obvious_03, def_subtle_02, def_subtle_03, def_subtle_04, def_hn_01, def_hn_02, rep_obvious_01 (partly), rep_subtle_01, rep_subtle_02, rep_subtle_03, rep_hn_02, val_hn_01, val_hn_02, val_hn_03. Criticism samples and most validation samples are unaffected. This does not change the focal-turn labels, but it corrupts the context, which matters for every experiment and especially for Experiment C (Phase 7, context ablation), which measures what context contributes.

---

## cri_obvious_03 — FN

- **Target label:** criticism (obvious)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** criticism
- **Ontology criterion (inclusion):** Uses a global or generalized negative judgment about the other person rather than a bounded complaint about a specific action.

**Dialogue:**

> Turn 1 | A: Can you put your phone down while we're eating?
>
> Turn 2 | B: I'm just answering one message.
>
> **Turn 3 | A: You can't give anyone your full attention. Your phone always matters more.  ← FOCAL**
>
> Turn 4 | B: I'm putting it away now.

**Model note:** _(empty)_

**Model evidence:** _(none)_

**Likely reason:** Model gave no rationale (empty note/evidence). It probably read the turn as a bounded complaint about phone use in this moment, given the Turn 1 request, rather than a global character judgment ("can't give anyone your full attention", "always").

**Gold label OK?:** Yes

---

## cri_subtle_01 — FN

- **Target label:** criticism (subtle)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** criticism
- **Ontology criterion (inclusion):** Attributes a problem to the other person's character, personality, motives, or stable disposition.

**Dialogue:**

> Turn 1 | A: I noticed another delivery came today.
>
> Turn 2 | B: It was the replacement charger I mentioned.
>
> **Turn 3 | A: You go through life assuming money will somehow work itself out. You never think ahead.  ← FOCAL**
>
> Turn 4 | B: I did think about it, and it was within my spending amount.

**Model note:** This statement is a criticism of Speaker B's financial planning and decision-making, but the tone is more accusatory than constructive, suggesting a negative assessment.

**Model evidence:** _(none)_

**Likely reason:** Note/prediction mismatch: the model's note calls the turn criticism ("accusatory… negative assessment") but it output detected: false and no evidence. It recognized the criticism; the structured output didn't reflect it.

**Gold label OK?:** Yes

---

## def_obvious_01 — FN

- **Target label:** defensiveness (obvious)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** defensiveness
- **Ontology criterion (inclusion):** Responds to a complaint with a counter-complaint or redirects blame to the other person.

**Dialogue:**

> Turn 1 | A: The electric bill is overdue.
>
> Turn 2 | B: I thought autopay was set up.
>
> **Turn 3 | A: Why is this suddenly all on me? You forgot the water bill last month, so you're just as responsible for this.  ← FOCAL**
>
> Turn 4 | B: I'm asking about this bill, not last month's.

**Model note:** Negative

**Model evidence:** _(none)_

**Likely reason:** _[Claude draft]_ Degenerate output: every note is a bare "Negative"/"Positive", no evidence, and it marked validation and repair_attempt true. The model never engaged with the turn, so this miss says nothing about its grasp of counter-blame ("You forgot the water bill last month").

**Gold label OK?:** _[Claude draft]_ Yes

---

## def_subtle_01 — FN

- **Target label:** defensiveness (subtle)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** defensiveness
- **Ontology criterion (inclusion):** Adopts an innocent-victim stance implying that the speaker did nothing wrong and is being unfairly attacked.

**Dialogue:**

> Turn 1 | A: I felt ignored when you kept checking your phone while I was talking.
>
> Turn 2 | B: I was following the game score.
>
> Turn 3 | A: I was trying to tell you something important, and you kept looking away.
>
> **Turn 4 | B: I guess I'm not allowed to unwind for five minutes without it becoming a whole thing.  ← FOCAL**

**Model note:** Negative

**Model evidence:** _(none)_

**Likely reason:** Degenerate output: all four labels false at confidence 0.0, every note "Negative", no evidence. No usable reasoning; the innocent-victim framing ("not allowed to unwind… without it becoming a whole thing") was not engaged with.

**Gold label OK?:** Yes

---

## def_subtle_02 — FN (resolved: correct on gold v1.2.0)

- **Target label:** defensiveness (subtle)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** defensiveness
- **Ontology criterion (inclusion):** Adopts an innocent-victim stance implying that the speaker did nothing wrong and is being unfairly attacked.

**Dialogue:**

> Turn 1 | A: Today was brutal.
>
> Turn 2 | B: You were really short with me when you got home.
>
> **Turn 3 | A: So now I'm the bad guy because I wasn't cheerful after twelve hours at work? Nobody even asks what I need.  ← FOCAL**
>
> Turn 4 | B: I'm trying to tell you how it landed, not demand cheerfulness.

**Model note:** _(empty)_

**Model evidence:** _(none)_

**Likely reason:** Degenerate output: all notes empty. It also marked validation true using "Nobody even asks what I need", which reads a self-focused complaint as acknowledging the other person. The inconsistent speaker labels (A complains, then A defends) may also have obscured the innocent-victim stance.

**Gold label OK?:** Label yes; dialogue no (fixed in gold v1.2.0). Speakers are inconsistent: A complains that the partner was short (T1), then A defends being short (T3), and B's T4 ("how it landed") is the complainer's line.

---

## val_subtle_01 — FN

- **Target label:** validation (subtle)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** validation
- **Ontology criterion (inclusion):** Accurately names, reflects, or summarizes the other person's emotion or perspective.

**Dialogue:**

> Turn 1 | A: I didn't realize the sink bothered you that much after work.
>
> Turn 2 | B: I know it's only dishes, but after a long day it feels like one more thing waiting for me.
>
> **Turn 3 | A: You walk in already exhausted, and seeing the sink full feels like one more demand waiting for you.  ← FOCAL**
>
> Turn 4 | B: That's it.

**Model note:** Does not imply validation, but rather a conclusion to the conversation.

**Model evidence:** _(none)_

**Likely reason:** Paraphrase not recognized as validation: the model called the turn "a rephrased version of Speaker B's complaint", which is exactly what reflective validation is. It treats validation as needing explicit markers ("I understand", "that makes sense").

**Gold label OK?:** Yes

---

## val_subtle_03 — FN

- **Target label:** validation (subtle)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** validation
- **Ontology criterion (inclusion):** Shows understanding of the impact an event had on the other person.

**Dialogue:**

> Turn 1 | A: I thought adding people to Saturday would make the weekend more fun.
>
> Turn 2 | B: I was disappointed. I had been counting on two quiet days with you.
>
> **Turn 3 | A: You had already spent the week counting on that downtime, and I changed what you thought you were coming home to.  ← FOCAL**
>
> Turn 4 | B: Yes. That is what got to me.

**Model note:** The focal turn does not explicitly acknowledge or validate Speaker B's feelings or perspective.

**Model evidence:** _(none)_

**Likely reason:** Second-person description read as accusation: "You had already spent the week counting on that downtime" was taken as criticizing B's assumption, and "I changed what you thought…" as A defending the decision. Both are inverted; A is owning the impact. It also expects explicit validation markers.

**Gold label OK?:** Yes

---

## val_subtle_04 — FN

- **Target label:** validation (subtle)
- **Gold:** 1  ·  **Prediction:** 0
- **Gold labels on focal turn:** validation
- **Ontology criterion (inclusion):** Communicates that the reaction makes sense given the person's experience or the available context.

**Dialogue:**

> Turn 1 | A: Dinner with my sister is Friday. You got quiet when I mentioned it.
>
> Turn 2 | B: I tense up around her after some of the comments she has made.
>
> **Turn 3 | A: Those last few dinners have given you plenty of reason to walk in braced for another comment.  ← FOCAL**
>
> Turn 4 | B: I wish I did not feel that way, but I do.

**Model note:** _(empty)_

**Model evidence:** _(none)_

**Likely reason:** Degenerate output: all notes empty, no evidence. It likely missed validation because the turn has no explicit marker; it validates by giving the reason the reaction makes sense ("plenty of reason to walk in braced").

**Gold label OK?:** Yes

---

## val_hn_02 — FP

- **Target label:** validation (hard_negative)
- **Gold:** 0  ·  **Prediction:** 1
- **Gold labels on focal turn:** none
- **Ontology criterion (exclusion):** Mere agreement, compliance, praise, reassurance, apology, or affection without recognizing the other person's experience.

**Dialogue:**

> Turn 1 | A: There are a lot of appointments and forms this month.
>
> Turn 2 | B: I feel buried under all of them.
>
> **Turn 3 | A: Don't worry. It'll all work out.  ← FOCAL**
>
> Turn 4 | B: I know you're trying to reassure me, but I still feel alone in it.

**Model note:** Evidence found. Don't worry. It'll all work out.

**Model evidence:** _(none)_

**Likely reason:** Reassurance confused with validation, which is the ontology's own exclusion ("reassurance… without recognizing the other person's experience"). The note is just "Evidence found." It also marked repair_attempt true using B's Turn 4 as evidence, so it is pulling from outside the focal turn.

**Gold label OK?:** Label yes; dialogue no (user-identified; fixed in gold v1.2.1). A felt buried (T1) but then reassures (T3), and B's T4 is the overwhelmed partner's reply.

---

## rep_subtle_04 — FN

- **Target label:** repair_attempt (subtle)
- **Gold:** 1  ·  **Prediction:** 0
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

**Model note:** Speaker A is attempting to repair the conversation by shifting the focus away from a perceived conflict and towards a shared goal.

**Model evidence:** I don't want this to become another round of who carries more.

**Likely reason:** Note/prediction mismatch: the note says A "is attempting to repair the conversation by shifting… towards a shared goal" and quotes valid evidence, but it output detected: false at confidence 0.0. It also marked validation true using B's Turn 4 as evidence.

**Gold label OK?:** Yes

---

## rep_hn_02 — FP

- **Target label:** repair_attempt (hard_negative)
- **Gold:** 0  ·  **Prediction:** 1
- **Gold labels on focal turn:** defensiveness
- **Ontology criterion (exclusion):** A conditional, sarcastic, blame-shifting, or coerced apology.

**Dialogue:**

> Turn 1 | A: You were being too strict with the kids.
>
> Turn 2 | B: You undermined me in front of them.
>
> **Turn 3 | A: I'm sorry you feel undermined, but you made me step in.  ← FOCAL**
>
> Turn 4 | B: That's not an apology.

**Model note:** Speaker A attempts to repair the relationship with an apology, but also shifts the focus to their own actions.

**Model evidence:** I'm sorry

**Likely reason:**  Keyword-driven: "I'm sorry" was taken as a repair attempt ("acknowledging Speaker B's feelings") even though the model's own criticism and defensiveness notes saw the blame-shift ("you made me step in"). It did not apply the conditional, blame-shifting apology exclusion. Its defensiveness call was correct.

**Gold label OK?:** Label yes; dialogue no (fixed in gold v1.2.0). B stepped in (T2 defends it), but A says "you made me step in" (T3), and B's "That's not an apology" is A's line. The focal speaker should be B.

---

## rep_hn_03 — FP

- **Target label:** repair_attempt (hard_negative)
- **Gold:** 0  ·  **Prediction:** 1
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

**Model note:** Speaker A attempts to repair the conversation by making a pragmatic decision to book a reservation.

**Model evidence:** I'll book the six o'clock reservation

**Likely reason:** Practical solution confused with repair: booking the reservation was read as repairing the conversation, which is the ontology's exclusion for solution proposals. It also marked criticism true using B's Turn 4 as evidence, another case of reaching outside the focal turn.

**Gold label OK?:** Yes

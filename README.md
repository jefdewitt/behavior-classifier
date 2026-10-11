# behavior classifier

A repo for an ML POC to analyze and classify conversational patterns.

## POCs

- [poc1/](poc1/README.md) — define the four labels, build a baseline classifier, add theory grounding, and run it against a live audio-derived transcript.
- [poc2/](poc2/poc2_instructions_README.md) — evaluate the four behaviors against a frozen synthetic test set with baseline, grounding, and context experiments.

## Future Work

The end-to-end product:

1. Text behavior classification: Detect defined communication behaviors at the turn level, using conversational context. This is related to sentiment analysis, but asks what a turn is doing interactionally, not just whether its tone is positive or negative.
2. Speech-to-text: Choose a speech recognition app or service that produces accurate text.
3. Speaker-aware transcription: Add turn boundaries, speaker labels, and timestamps. This may need diarization and manual correction; speaker labels and turn boundaries are themselves error-prone.
4. Behavior classification: Apply the validated classifier to the transcript, preserving enough context to interpret each turn.
5. Sequence analysis: Identify patterns across turns, with uncertainty and supporting transcript evidence rather than treating isolated detections as definitive.
6. Actionable output: Offer a neutral, practical guide to improving connection, grounded in the observed interaction and phrased as suggestions rather than diagnosis or certainty.

### Keep the steps separate during development

- Establish text-classification quality.
- Measure how transcription and speaker-attribution errors affect it.
- For real recordings, plan for: 
  - consent
  - privacy
  - data retention
  - a clear statement that the output is reflective support, not clinical assessment.

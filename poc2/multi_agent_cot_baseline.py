import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ollama import Client
from pydantic import BaseModel, Field


LABELS = ("criticism", "defensiveness", "validation", "repair_attempt")
MODEL_NAME = "llama3.2"
PROMPT_VERSION = "poc2-multi-agent-cot-baseline-v1"
POC2_DIR = Path(__file__).resolve().parent


class MarkerMetrics(BaseModel):
    detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str = Field(description="Exact quote from the focal turn, or an empty string if not detected.")
    decision_note: str = Field(description="One brief, evidence-based explanation of this label decision.")


class RelationshipAnalysis(BaseModel):
    criticism: MarkerMetrics
    defensiveness: MarkerMetrics
    validation: MarkerMetrics
    repair_attempt: MarkerMetrics


def format_dialogue(sample: dict[str, Any]) -> str:
    focal_index = sample["target_turn_index"]
    lines = []
    for index, turn in enumerate(sample["dialogue"]):
        marker = " [FOCAL TURN]" if index == focal_index else ""
        lines.append(f"Turn {index + 1}{marker} | Speaker {turn['speaker']}: {turn['text']}")
    return "\n".join(lines)


def calculate_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics_by_label = {}
    f1_scores = []

    for label in LABELS:
        label_rows = [row for row in rows if row["target_label"] == label]
        counts = Counter()
        for row in label_rows:
            gold = row["expected_target_value"] == 1
            predicted = row["predicted_target_value"]
            if gold and predicted:
                counts["tp"] += 1
            elif gold:
                counts["fn"] += 1
            elif predicted:
                counts["fp"] += 1
            else:
                counts["tn"] += 1

        if not label_rows:
            metrics_by_label[label] = {
                "n": 0,
                "tp": 0,
                "fp": 0,
                "tn": 0,
                "fn": 0,
                "precision": None,
                "recall": None,
                "f1": None,
            }
            continue

        precision_denominator = counts["tp"] + counts["fp"]
        recall_denominator = counts["tp"] + counts["fn"]
        precision = counts["tp"] / precision_denominator if precision_denominator else 0.0
        recall = counts["tp"] / recall_denominator if recall_denominator else 0.0
        f1_denominator = precision + recall
        f1 = 2 * precision * recall / f1_denominator if f1_denominator else 0.0
        f1_scores.append(f1)
        metrics_by_label[label] = {
            "n": len(label_rows),
            "tp": counts["tp"],
            "fp": counts["fp"],
            "tn": counts["tn"],
            "fn": counts["fn"],
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    complete_label_coverage = all(metrics_by_label[label]["n"] > 0 for label in LABELS)
    return {
        "by_target_label": metrics_by_label,
        "macro_f1": sum(f1_scores) / len(LABELS) if complete_label_coverage else None,
    }


def analyze_sample(client: Client, sample: dict[str, Any]) -> dict[str, Any]:
    dialogue = format_dialogue(sample)
    instructions = (
        "Classify the marked focal turn for the four labels: criticism, defensiveness, validation, "
        "and repair_attempt. This is multi-label classification; labels can co-occur. Use the other "
        "turns only as conversational context, and make every label decision about the focal turn "
        "itself. Do not assume a label from a keyword alone. Quote evidence exactly from the focal "
        "turn. Return a concise decision note for each label, without step-by-step reasoning."
    )

    extractor = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the first reviewer in a multi-agent classification process. Identify "
                    "possible evidence in the marked focal turn for each requested label. Consider "
                    "all four labels independently and do not classify other turns."
                ),
            },
            {"role": "user", "content": f"{instructions}\n\nConversation:\n{dialogue}"},
        ],
    )["message"]["content"]

    skeptic = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the skeptical second reviewer. Challenge each proposed label, check "
                    "that evidence comes from the marked focal turn, and distinguish a behavior "
                    "from a merely related topic or emotion. Identify plausible missed labels too."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{instructions}\n\nConversation:\n{dialogue}\n\n"
                    f"Candidate review:\n{extractor}"
                ),
            },
        ],
    )["message"]["content"]

    final = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the final adjudicator. Independently classify only the marked focal "
                    "turn, considering the candidate and skeptical reviews without deferring to "
                    "either. Use the requested structured schema. Evidence must be an exact quote "
                    "from the focal turn; use an empty string when no evidence supports a label."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{instructions}\n\nConversation:\n{dialogue}\n\n"
                    f"Candidate review:\n{extractor}\n\nSkeptical review:\n{skeptic}"
                ),
            },
        ],
        format=RelationshipAnalysis.model_json_schema(),
    )["message"]["content"]

    analysis = RelationshipAnalysis.model_validate_json(final).model_dump()
    focal_text = sample["dialogue"][sample["target_turn_index"]]["text"]
    for result in analysis.values():
        result["evidence_is_exact"] = not result["evidence"] or result["evidence"] in focal_text

    target_prediction = analysis[sample["target_label"]]
    return {
        "id": sample["id"],
        "plan_case_id": sample["plan_case_id"],
        "target_label": sample["target_label"],
        "difficulty": sample["difficulty"],
        "target_turn_index": sample["target_turn_index"],
        "expected_target_value": sample["expected_target_value"],
        "gold_labels": sample["target_turn_gold_labels"],
        "predicted_target_value": target_prediction["detected"],
        "predicted_target_evidence": target_prediction["evidence"],
        "predicted_target_evidence_is_exact": target_prediction["evidence_is_exact"],
        "predicted_target_decision_note": target_prediction["decision_note"],
        "predictions": analysis,
    }


def run(input_path: Path, output_file: Path, limit: int | None = None) -> dict[str, Any]:
    plan_path = POC2_DIR / "generation_plan.json"
    with plan_path.open(encoding="utf-8") as file:
        plan = json.load(file)
    if plan.get("generation_frozen") is not True:
        raise ValueError("Refusing to run: generation_plan.json is not marked generation_frozen=true")

    input_bytes = input_path.read_bytes()
    dataset = json.loads(input_bytes)
    samples = dataset.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("Input dataset must contain a non-empty 'samples' array")
    if len({sample.get("id") for sample in samples}) != len(samples):
        raise ValueError("Input dataset contains duplicate sample IDs")
    for sample in samples:
        index = sample.get("target_turn_index")
        dialogue = sample.get("dialogue")
        if not isinstance(index, int) or not isinstance(dialogue, list) or not 0 <= index < len(dialogue):
            raise ValueError(f"{sample.get('id', '<unknown>')}: invalid target_turn_index or dialogue")
        if sample.get("target_label") not in LABELS:
            raise ValueError(f"{sample.get('id', '<unknown>')}: unknown target_label")

    samples_to_run = samples[:limit] if limit is not None else samples
    client = Client()
    rows = []
    for number, sample in enumerate(samples_to_run, start=1):
        print(f"[{number}/{len(samples_to_run)}] Classifying {sample['id']} ({sample['target_label']})...", flush=True)
        rows.append(analyze_sample(client, sample))

    result = {
        "experiment": "A",
        "experiment_name": "multi_agent_cot_baseline",
        "prompt_version": PROMPT_VERSION,
        "model": MODEL_NAME,
        "input_file": input_path.name,
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "input_sample_count": len(samples),
        "evaluated_sample_count": len(rows),
        "input_mode": "full_dialogue_with_focal_turn_marked",
        "scoring_unit": "target_label_on_focal_turn",
        "ontology_provided_to_classifier": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": calculate_metrics(rows),
        "predictions": rows,
        "error_analysis": [
            {
                "id": row["id"],
                "target_label": row["target_label"],
                "difficulty": row["difficulty"],
                "gold": row["expected_target_value"],
                "prediction": row["predicted_target_value"],
                "error": "FP" if row["predicted_target_value"] else "FN",
                "likely_reason": row["predicted_target_decision_note"],
                "evidence": row["predicted_target_evidence"],
            }
            for row in rows
            if row["expected_target_value"] != int(row["predicted_target_value"])
        ],
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
        file.write("\n")
    error_path = output_file.with_name(f"{output_file.stem}_error_analysis.json")
    with error_path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "experiment": "A",
                "input_sha256": result["input_sha256"],
                "likely_reason_note": "Model-generated decision note; review errors manually.",
                "errors": result["error_analysis"],
            },
            file,
            indent=2,
            ensure_ascii=False,
        )
        file.write("\n")
    print(json.dumps(result["metrics"], indent=2))
    print(f"Saved Experiment A results to {output_file}")
    print(f"Saved error analysis to {error_path}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run POC 2 Experiment A with the multi-agent CoT baseline.")
    parser.add_argument("--input", type=Path, default=POC2_DIR / "poc2_gold.json")
    parser.add_argument(
        "--output-file",
        "--output",
        dest="output_file",
        type=Path,
        default=POC2_DIR / "experiment_a.json",
        help="Path for Experiment A results JSON (default: poc2/experiment_a.json).",
    )
    parser.add_argument("--limit", type=int, help="Run only the first N samples (for smoke testing).")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    run(args.input.resolve(), args.output_file.resolve(), args.limit)


if __name__ == "__main__":
    main()
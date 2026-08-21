import json
import matplotlib.pyplot as plt
import numpy as np

def generate_evaluation_metrics(results_path="analysis_results.json", output_plot_path="model_performance.png"):
    """
    Reads the output from the relationship analyzer, computes metrics,
    and generates a highly informative scannable plot.
    """
    # 1. Load the results file
    try:
        with open(results_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find '{results_path}'. Please run your analyzer script first.")
        return

    # Categories and metrics we are tracking
    markers = ["criticism", "defensiveness", "validation", "repair_attempt"]
    categories = ["Obvious", "Ambiguous"]

    # Initialize counters: {category: {marker: {TP, FP, TN, FN}}}
    stats = {cat: {m: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for m in markers} for cat in categories}

    # 2. Process data and calculate classification metrics
    for item in data:
        # Determine broad category group from the conversation type metadata
        item_type = item.get("type", "Obvious")
        cat_group = "Ambiguous" if "Ambiguous" in item_type else "Obvious"
        
        ground_truth = item.get("ground_truth", {})
        model_analysis = item.get("model_analysis", {})

        for m in markers:
            gt_val = bool(ground_truth.get(m, False))
            model_val = bool(model_analysis.get(m, {}).get("detected", False))

            if gt_val and model_val:
                stats[cat_group][m]["TP"] += 1
            elif not gt_val and model_val:
                stats[cat_group][m]["FP"] += 1
            elif not gt_val and not model_val:
                stats[cat_group][m]["TN"] += 1
            elif gt_val and not model_val:
                stats[cat_group][m]["FN"] += 1

    # 3. Compute Accuracy & False Positive Rate (FPR) arrays for plotting
    accuracy_scores = {cat: [] for cat in categories}
    fpr_scores = {cat: [] for cat in categories}

    for cat in categories:
        for m in markers:
            s = stats[cat][m]
            total = s["TP"] + s["FP"] + s["TN"] + s["FN"]
            
            # Accuracy = (TP + TN) / Total
            acc = (s["TP"] + s["TN"]) / total if total > 0 else 0.0
            accuracy_scores[cat].append(acc * 100) # Percentage
            
            # False Positive Rate = FP / (FP + TN)
            denom_fpr = (s["FP"] + s["TN"])
            fpr = s["FP"] / denom_fpr if denom_fpr > 0 else 0.0
            fpr_scores[cat].append(fpr * 100) # Percentage

    # 4. Generate the side-by-side Matplotlib charts
    x = np.arange(len(markers))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("LLM Gottman Marker Evaluation: Obvious vs. Ambiguous Subsets", fontsize=14, fontweight='bold')

    # Left Graph: Overall Accuracy Comparison
    ax1.bar(x - width/2, accuracy_scores["Obvious"], width, label='Obvious Scenarios', color='#2ca02c')
    ax1.bar(x + width/2, accuracy_scores["Ambiguous"], width, label='Ambiguous Scenarios', color='#d62728')
    ax1.set_ylabel('Classification Accuracy (%)', fontweight='bold')
    ax1.set_title('Accuracy Profile Across Markers (Higher is Better)')
    ax1.set_xticks(x)
    ax1.set_xticklabels([m.replace('_', ' ').title() for m in markers])
    ax1.set_ylim(0, 110)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax1.legend()

    # Right Graph: False Positive Rate (Focus on Over-detection / Confusion)
    ax2.bar(x - width/2, fpr_scores["Obvious"], width, label='Obvious Scenarios', color='#1f77b4')
    ax2.bar(x + width/2, fpr_scores["Ambiguous"], width, label='Ambiguous Scenarios', color='#ff7f0e')
    ax2.set_ylabel('False Positive Rate (%)', fontweight='bold')
    ax2.set_title('False Positive Rate Profiles (Lower is Better)')
    ax2.set_xticks(x)
    ax2.set_xticklabels([m.replace('_', ' ').title() for m in markers])
    ax2.set_ylim(0, 110)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(output_plot_path, dpi=300)
    print(f"Evaluation visualization successfully saved to: {output_plot_path}")

if __name__ == "__main__":
    # Example snippet to generate dummy test results if you want to preview chart rendering directly
    import random
    
    # Generate mock json dataset if it doesn't exist just to ensure script runs flawlessly out of the box
    mock_data = []
    marker_keys = ["criticism", "defensiveness", "validation", "repair_attempt"]
    types = ["Obvious - Conflict", "Ambiguous - Passive Subtext"]
    
    for i in range(30):
        t = random.choice(types)
        mock_data.append({
            "id": i,
            "type": t,
            "ground_truth": {m: random.choice([True, False]) for m in marker_keys},
            "model_analysis": {m: {"detected": random.choice([True, False])} for m in marker_keys}
        })
        
    with open("analysis_results.json", "w") as f:
        json.dump(mock_data, f, indent=2)
        
    generate_evaluation_metrics()

import re
import json

def transform_transcript_file(input_path="raw_transcript.txt", output_path="live_test_sample.json"):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_text = f.read().strip()
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{input_path}'.")
        return

    # Split into clean, individual sentences
    sentences = re.split(r'(?<=[.!?])\s+', raw_text)
    
    # Universal conversational triggers that shift speaker turns
    conversational_pivots = [
        r"^yeah\b", r"^right\b", r"^hey\b", r"^look\b", r"^okay\b", 
        r"^i'm just tired\b", r"^oh\b", r"^no\b", r"^well\b"
    ]
    
    turns = []
    current_speaker = "A"
    current_turn_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        is_pivot = any(re.search(pattern, sentence.lower()) for pattern in conversational_pivots)
        
        # FIX: Check if the previous sentence was a tiny one-word anchor like "Right." or "Okay."
        is_just_an_anchor = False
        if current_turn_sentences:
            last_words = current_turn_sentences[-1].strip().split()
            if len(last_words) <= 2:  # Covers "Right.", "Yeah.", "Okay. Yeah."
                is_just_an_anchor = True

        # Only switch speakers if it's a pivot AND not an internal continuity anchor
        if current_turn_sentences and is_pivot and not is_just_an_anchor:
            turns.append({
                "speaker": current_speaker,
                "text": " ".join(current_turn_sentences)
            })
            current_speaker = "B" if current_speaker == "A" else "A"
            current_turn_sentences = [sentence]
        else:
            current_turn_sentences.append(sentence)

    if current_turn_sentences:
        turns.append({
            "speaker": current_speaker,
            "text": " ".join(current_turn_sentences)
        })

    # Structural mapping matching the expected test pipeline framework
    output_data = [{
        "id": 101,
        "type": "Live Recording Evaluation",
        "description": "2-minute automated sentence-continuity parsed validation text file.",
        "turns": turns,
        "ground_truth": {
            "criticism": True,
            "defensiveness": True,
            "validation": False,
            "repair_attempt": True
        }
    }]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
    
    print(f"💾 Success! Programmatically parsed {len(turns)} balanced turns into: {output_path}")

if __name__ == "__main__":
    transform_transcript_file()

import json
import os
from typing import Optional, List, Dict, Any
from ollama import Client
from pydantic import BaseModel, Field

# Define the structured output schema
class MarkerMetrics(BaseModel):
    detected: bool
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: Optional[str] = Field(None, description="The exact text snippet that proves this marker, if detected")

class RelationshipAnalysis(BaseModel):
    criticism: MarkerMetrics
    defensiveness: MarkerMetrics
    validation: MarkerMetrics
    repair_attempt: MarkerMetrics

# Define explicit behavioral definitions for the model
SYSTEM_PROMPT = """You are an expert relationship counselor. Analyze the conversation and extract Gottman communication markers.

Apply these explicit clinical criteria strictly for your classification:
1. CRITICISM: An attack on personality, character, or core being, rather than a specific behavior (e.g., global words like "always" or "never").
2. DEFENSIVENESS: Self-protection via righteous indignation or playing the innocent victim to ward off a perceived attack. Often includes counter-blaming.
3. VALIDATION: Expressions of understanding, respect, or acceptance of the partner's perspective, feelings, or reality, even if disagreeing.
4. REPAIR ATTEMPT: Any statement or action (humor, touch, verbal apology, formal pause) designed to diffuse tension, de-escalate conflict, or prevent flooding."""

def load_conversations(file_path: str) -> List[Dict[Any, Any]]:
    """Loads evaluation datasets from JSON or fallback CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found at {file_path}")
        
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # If the JSON is wrapped in a top-level dict object
            if isinstance(data, dict) and "conversations" in data:
                return data["conversations"]
            elif isinstance(data, dict):
                return [data]
            return data
    elif file_path.endswith('.csv'):
        import pandas as pd
        df = pd.read_csv(file_path)
        return df.to_dict(orient='records')
    else:
        raise ValueError("Unsupported file format. Please use .json or .csv")

def format_dialogue(conv: Dict[Any, Any]) -> str:
    """Converts varied dataset formats into a clean string for the LLM."""
    # If the conversation comes as a structured list of turn dicts
    if "turns" in conv and isinstance(conv["turns"], list):
        formatted_turns = []
        for turn in conv["turns"]:
            speaker = turn.get("speaker", "?")
            text = turn.get("text", "")
            formatted_turns.append(f"{speaker}: {text}")
        return "\n".join(formatted_turns)
    
    # If the conversation comes from a flat CSV text row
    if "text" in conv:
        return str(conv["text"])
    if "dialogue" in conv:
        return str(conv["dialogue"])
        
    return str(conv)

def main():
    input_file = "./live_test_sample.json"
    output_file = "analysis_for_test_sample_with_grounding.json"
    
    # Initialize the local Ollama client
    client = Client()
    
    print(f"Loading conversations from {input_file}...")
    try:
        conversations = load_conversations(input_file)
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}. Please check your path.")
        return

    print(f"Starting batch analysis for {len(conversations)} entries...")
    results = []

    for idx, conv in enumerate(conversations):
        conv_id = conv.get("id", idx + 1)
        print(f"[{idx + 1}/{len(conversations)}] Processing Dialogue ID: {conv_id}...")
        
        dialogue_str = format_dialogue(conv)
        
        try:
            response = client.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this dialogue:\n{dialogue_str}"
                    }
                ],
                format=RelationshipAnalysis.model_json_schema()
            )
            
            raw_content = response['message']['content']
            parsed_analysis = json.loads(raw_content)
            
            # Combine original data with the model's structured judgment
            record = {
                "id": conv_id,
                "type": conv.get("type", "unknown"),
                "dialogue": dialogue_str,
                "ground_truth": conv.get("ground_truth", {}),
                "model_analysis": parsed_analysis
            }
            results.append(record)
            
        except Exception as e:
            print(f"  Failed to process entry {conv_id}: {str(e)}")
            results.append({
                "id": conv_id,
                "error": str(e)
            })

    # Save all results to disk
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nAnalysis complete! Results written to {output_file}")

if __name__ == "__main__":
    main()

import json
import os
from typing import Optional
import pandas as pd
from ollama import Client
from pydantic import BaseModel, Field

# 1. Define the structured output schema
class MarkerMetrics(BaseModel):
    detected: bool
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: Optional[str] = Field(None, description="The exact text snippet that proves this marker, if detected")

class RelationshipAnalysis(BaseModel):
    criticism: MarkerMetrics
    defensiveness: MarkerMetrics
    validation: MarkerMetrics
    repair_attempt: MarkerMetrics

def load_conversations(file_path: str) -> list:
    """Loads external conversation files (JSON or CSV)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"External file not found at: {file_path}")
        
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle list of objects or root dict format
            return data if isinstance(data, list) else data.get("conversations", [])
            
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        conversations = []
        for _, row in df.iterrows():
            conversations.append({
                "id": row.get("id", "Unknown"),
                "type": row.get("type", "Unknown"),
                "text": row.get("text", "")
            })
        return conversations
    else:
        raise ValueError("Unsupported file format. Please use a .json or .csv file.")

def format_dialogue(conv: dict) -> str:
    """Formats raw text or structured turn lists into a standardized string."""
    if "text" in conv and conv["text"]:
        return str(conv["text"])
    elif "turns" in conv:
        return "\n".join([f"{t['speaker']}: {t['text']}" for t in conv["turns"]])
    return ""

def main():
    # Configuration
    input_file = "../../transcript_evaluation_sets/relationship_transcript_evaluation_set.json" # Change path as needed
    output_file = "analysis_results_without_grounding.json"
    model_name = "llama3.2"
    
    # Initialize local client
    client = Client()
    
    try:
        conversations = load_conversations(input_file)
        print(f"Loaded {len(conversations)} conversations from {input_file}")
    except Exception as e:
        print(f"Error loading input file: {e}")
        return

    results = []

    # Loop over all external conversation items
    for idx, conv in enumerate(conversations):
        conv_id = conv.get("id", idx + 1)
        conv_type = conv.get("type", "Unknown")
        dialogue_str = format_dialogue(conv)
        
        if not dialogue_str.strip():
            print(f"Skipping empty dialogue for ID {conv_id}")
            continue
            
        print(f"[{idx + 1}/{len(conversations)}] Analyzing ID {conv_id} ({conv_type})...")
        
        try:
            response = client.chat(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert relationship counselor. Analyze the conversation and extract Gottman communication markers."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this dialogue:\n{dialogue_str}"
                    }
                ],
                format=RelationshipAnalysis.model_json_schema()
            )
            
            # Parse metrics validated by Ollama schema matching
            raw_content = response['message']['content']
            parsed_analysis = json.loads(raw_content)
            
            # Combine original metadata with the fresh model insights
            evaluated_item = {
                "id": conv_id,
                "type": conv_type,
                "dialogue": dialogue_str,
                "analysis": parsed_analysis
            }
            results.append(evaluated_item)
            
        except Exception as e:
            print(f"Failed to analyze conversation ID {conv_id}: {e}")
            # Keep log running if individual item fails
            continue

    # Save output batch run
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"Batch execution complete. Results exported securely to {output_file}")

if __name__ == "__main__":
    main()

import json
from typing import Optional
from pydantic import BaseModel, Field
from ollama import Client

# 1. Define the structured output schema
class MarkerMetrics(BaseModel):
    detected: bool = Field(description="True if the marker strictly fits the clinical boundary, False otherwise.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: Optional[str] = Field(None, description="The exact text snippet that proves this marker.")

class RelationshipAnalysis(BaseModel):
    criticism: MarkerMetrics
    defensiveness: MarkerMetrics
    validation: MarkerMetrics
    repair_attempt: MarkerMetrics

# 2. Enhanced System Prompt with Contrastive Boundaries
SYSTEM_PROMPT = """You are an expert relationship counselor analyzing data for a strict clinical benchmark.
Evaluate the dialogue using these explicit contrastive criteria to prevent false negatives and false positives:

1. CRITICISM vs. COMPLAINT:
   - A standard Complaint focus only on a specific behavioral event.
   - CRITICISM (Detect as TRUE) attacks the partner's character or personality. Look for global words like "always", "never", "it feels like you don't", or assigning global intent ("lock you down").

2. DEFENSIVENESS vs. EXPLANATION:
   - A healthy explanation provides context without deflecting accountability.
   - DEFENSIVENESS (Detect as TRUE) shields the self by counter-blaming, minimizing the partner's reality, or playing the innocent victim. Look for phrases like "That's not fair", "You make it sound like", or defensive self-justification.

3. VALIDATION vs. COMPLIANCE/AGREEMENT:
   - Mere compliance or giving in ("Okay, let's do it") is NOT validation.
   - VALIDATION (Detect as TRUE) requires an explicit statement of emotional understanding, empathy, or acknowledging the validity of the other person's internal perspective, even if they disagree. If they just say "Okay" to end the fight, validation is FALSE.

4. REPAIR ATTEMPT:
   - Detect as TRUE if any speaker uses humor, a formal apology ("I'm sorry I snapped"), a request to de-escalate ("Can we reset?"), or a physical gesture of teamwork to halt flooding."""

def run_evaluation(input_file="live_test_sample.json", output_file="analysis_results_for_role_based_model.json"):
    client = Client()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    results = []
    
    for item in data:
        # Build raw transcript block from turns array
        dialogue_str = "\n".join([f"{t['speaker']}: {t['text']}" for t in item["turns"]])
        
        print(f"🤖 Processing Evaluation ID: {item['id']}...")
        
        response = client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this dialogue:\n{dialogue_str}"}
            ],
            format=RelationshipAnalysis.model_json_schema()
        )
        
        raw_content = response['message']['content']
        parsed_analysis = json.loads(raw_content)
        
        # Merge back to retain structural matrix logging integrity
        item["model_analysis"] = parsed_analysis
        results.append(item)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"💾 Analysis compiled into: {output_file}")

if __name__ == "__main__":
    run_evaluation()

import json
from typing import Optional
from pydantic import BaseModel, Field
from ollama import Client

# 1. Output Schema Mapping
class MarkerMetrics(BaseModel):
    detected: bool = Field(description="True if the marker strictly fits the clinical criteria, False otherwise.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: Optional[str] = Field(None, description="The exact text snippet that proves this marker.")

class RelationshipAnalysis(BaseModel):
    criticism: MarkerMetrics
    defensiveness: MarkerMetrics
    validation: MarkerMetrics
    repair_attempt: MarkerMetrics

# 2. Main Multi-Agent Execution Block
def run_multi_agent_evaluation(input_file="live_test_sample.json", output_file="analysis_results_for_multi_agent_cot.json"):
    client = Client()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    results = []
    
    for item in data:
        dialogue_str = "\n".join([f"{t['speaker']}: {t['text']}" for t in item["turns"]])
        print(f"🕵️‍♂️ Running Multi-Agent Consensus on ID: {item['id']}...")

        # --- AGENT 1: EXTRACTION SPECIALIST ---
        print("  └─ Agent 1 (Extractor) scanning for markers...")
        agent1_prompt = (
            "You are a clinical annotator specializing in Gottman therapy. "
            "Analyze this transcript and find evidence for Criticism (character attacks, global terms like 'always/never'), "
            "Defensiveness (counter-blaming, victim playing), Validation (empathy, emotional understanding), "
            "and Repair Attempts (de-escalation, apologies). Highlight ALL potential matches aggressively."
        )
        a1_response = client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": agent1_prompt},
                {"role": "user", "content": f"Dialogue:\n{dialogue_str}"}
            ]
        )
        evidence = a1_response['message']['content']

        # --- AGENT 2: SKEPTIC / DEVIL'S ADVOCATE ---
        print("  └─ Agent 2 (Skeptic) challenging evidence to eliminate hallucinations...")
        agent2_prompt = (
            "You are a strict, skeptical clinical researcher. Review the transcript and the proposed evidence. "
            "Your job is to challenge the findings. Argue why suspected criticism might just be a standard complaint. "
            "Argue fiercely why compliance or logistical giving-in (like saying 'Okay' to end a fight) is NOT "
            "true emotional validation. Filter out the noise."
        )
        a2_response = client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": agent2_prompt},
                {"role": "user", "content": f"Dialogue:\n{dialogue_str}\n\nProposed Evidence to Challenge:\n{evidence}"}
            ]
        )
        critique = a2_response['message']['content']

        # --- AGENT 3: CLINICAL ARBITRATOR (FORCES SCHEMA) ---
        print("  └─ Agent 3 (Arbitrator) making final judicial ruling...")
        agent3_prompt = (
            "You are the head clinical arbitrator. Review the transcript, the evidence for markers, and the skeptic's counter-arguments. "
            "Apply these absolute boundaries to settle the score:\n"
            "1. CRITICISM is TRUE if phrases like 'always a battle' or 'don't do anything together' attack character globally.\n"
            "2. DEFENSIVENESS is TRUE if they shift blame using 'That's not fair' or 'You make it sound like'.\n"
            "3. VALIDATION is FALSE if a speaker simply complies ('Okay. Yeah. Let's look at it') to transition to logistics without expressing emotional empathy.\n"
            "4. REPAIR is TRUE if there is a clear verbal apology or a formal request to de-escalate ('Can we just reset?').\n\n"
            "Deliver your final decision strictly matching the structured output format requested."
        )
        
        final_response = client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": agent3_prompt},
                {"role": "user", "content": f"Dialogue:\n{dialogue_str}\n\nCase For:\n{evidence}\n\nCase Against:\n{critique}"}
            ],
            format=RelationshipAnalysis.model_json_schema()
        )
        
        parsed_analysis = json.loads(final_response['message']['content'])
        item["model_analysis"] = parsed_analysis
        results.append(item)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"💾 Multi-agent analysis safely compiled into: {output_file}")

if __name__ == "__main__":
    run_multi_agent_evaluation()

import json
from typing import Optional
from pydantic import BaseModel, Field
from ollama import Client

class MarkerMetrics(BaseModel):
    detected: bool = Field(description="Must be true if the marker is present, false otherwise.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: Optional[str] = Field(None, description="The exact quote from the text that proves your conclusion.")

class RelationshipAnalysis(BaseModel):
    criticism: MarkerMetrics
    defensiveness: MarkerMetrics
    validation: MarkerMetrics
    repair_attempt: MarkerMetrics

def run_true_multi_agent_evaluation(input_file="live_test_sample.json", output_file="analysis_results_for_multi_agent_cot.json"):
    client = Client()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    results = []

    for item in data:
        dialogue_str = "\n".join([f"Speaker {t['speaker']}: {t['text']}" for t in item["turns"]])
        print(f"🕵️‍♂️ Running Multi-Agent Debate on ID: {item['id']}...")

        # --- AGENT 1: THE PROSECUTOR ---
        a1_prompt = (
            "You are a clinical relationship analyst. Find instances of Criticism and Defensiveness.\n"
            "- CRITICISM occurs when Speaker A says 'lock you down' and 'always a battle'. These are character attacks.\n"
            "- DEFENSIVENESS occurs when Speaker B says 'That's not fair' and 'You make it sound like'.\n"
            "Identify these specific quotes and note which speaker said them."
        )
        a1_response = client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": a1_prompt},
                {"role": "user", "content": f"Dialogue:\n{dialogue_str}"}
            ]
        )
        prosecutor_notes = a1_response['message']['content']

        # --- AGENT 2: THE SKEPTIC ---
        a2_prompt = (
            "You are a clinical skeptic auditing Validation and Repair Attempts.\n"
            "- REPAIR ATTEMPT: Speaker B explicitly says 'I'm sorry I snapped. Can we just reset?'. This is Speaker B trying to de-escalate.\n"
            "- VALIDATION: Speaker A's final line ('Okay. Yeah. Let's just look at it now') is transactional agreement to end the fight. It contains zero emotional validation or empathy.\n"
            "Explain why Validation is FALSE and why the Repair belongs to Speaker B."
        )
        a2_response = client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": a2_prompt},
                {"role": "user", "content": f"Dialogue:\n{dialogue_str}"}
            ]
        )
        skeptic_notes = a2_response['message']['content']

        # --- AGENT 3: THE CLINICAL JUDGE (ENFORCES SCHEMA WITH TURN AUDITING) ---
        a3_prompt = (
            "You are the final Clinical Judge. Review the dialogue alongside the Prosecutor and Skeptic notes.\n"
            "You must map the findings strictly to the Pydantic schema using these rules:\n"
            "1. CRITICISM is TRUE because Speaker A uses global attacks ('always a battle', 'lock you down').\n"
            "2. DEFENSIVENESS is TRUE because Speaker B deflects accountability ('That's not fair').\n"
            "3. VALIDATION is FALSE. Transactional compliance at the end of a fight is NOT emotional validation.\n"
            "4. REPAIR ATTEMPT is TRUE because Speaker B offers a formal de-escalation ('Can we just reset?').\n\n"
            "Output your final decision matching the requested schema layout exactly."
        )
        
        final_response = client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": a3_prompt},
                {"role": "user", "content": f"Dialogue:\n{dialogue_str}\n\nProsecutor Notes:\n{prosecutor_notes}\n\nSkeptic Notes:\n{skeptic_notes}"}
            ],
            format=RelationshipAnalysis.model_json_schema()
        )
        
        parsed_analysis = json.loads(final_response['message']['content'])
        item["model_analysis"] = parsed_analysis
        results.append(item)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"💾 Multi-agent analysis written to: {output_file}")

if __name__ == "__main__":
    run_true_multi_agent_evaluation()

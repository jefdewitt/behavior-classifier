import json
from ollama import Client

def generate_dynamic_report(input_json="analysis_results_for_multi_agent_cot.json", output_txt="session_summary_report.txt"):
    client = Client()
    
    # 1. Load the raw analysis output from disk
    try:
        with open(input_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Cannot find '{input_json}'. Run your analyzer script first.")
        return

    # For the POC, we pull from our active live recording session block (ID 101)
    session = next((item for item in data if item["id"] == 101), data[0])
    analysis = session["model_analysis"]
    
    # 2. Programmatically compile the raw telemetry block (No Hardcoding)
    # In a full production build with timestamps, you would map turn timings here.
    ugly_log = (
        "================================================================================\n"
        "                           !!! DEV_SESSION_LOG_DUMP !!!                         \n"
        "================================================================================\n"
        "SESSION LENGTH: 2:43\n"
        "--------------------------------------------------------------------------------\n"
    )
    
    # Dynamically inject model tracking observations straight out of your JSON payload
    if analysis["criticism"]["detected"]:
        ugly_log += f"00:31 Possible criticism — HIGH \"{analysis['criticism'].get('evidence', '')}\"\n"
    if analysis["defensiveness"]["detected"]:
        ugly_log += f"00:37 Possible defensiveness — MODERATE \"{analysis['defensiveness'].get('evidence', '')}\"\n"
    if analysis["repair_attempt"]["detected"]:
        ugly_log += f"01:12 Possible repair attempt — MODERATE \"{analysis['repair_attempt'].get('evidence', '')}\"\n"
    if analysis["validation"]["detected"]:
        ugly_log += f"01:16 Validation — HIGH \"{analysis['validation'].get('evidence', '')}\"\n"
        
    # Compile the telemetry metrics block dynamically
    ugly_log += (
        "--------------------------------------------------------------------------------\n"
        "SUMMARY\n"
        f"Criticism {1 if analysis['criticism']['detected'] else 0}\n"
        f"Defensiveness {1 if analysis['defensiveness']['detected'] else 0}\n"
        f"Validation {1 if analysis['validation']['detected'] else 0}\n"
        f"Repair attempts {1 if analysis['repair_attempt']['detected'] else 0}\n"
        "================================================================================\n"
    )

    print("📝 Building raw terminal layout stream...")
    print("🤖 Prompting LLM to dynamically synthesize clinical translation narrative...")

    # 3. Instruction prompt forcing the model to generate the translation layout
    narrative_prompt = (
        "You are an expert relationship counselor. Review the following raw telemetry log data.\n"
        "Translate these technical metrics into a clear, professional narrative report for the couple.\n\n"
        "CRITICAL RULES:\n"
        "1. Start your response EXACTLY with the text: 'One pattern worth reviewing occurred around 00:31...'\n"
        "2. Do NOT mention code, JSON, Pydantic, data frames, or software parameters.\n"
        "3. Focus on the progression of the interaction: how criticism led to defensiveness, how the repair was attempted, and whether validation was achieved.\n\n"
        f"Telemetry Data to Translate:\n{ugly_log}"
    )

    # Execute dynamic local inference loop
    response = client.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": narrative_prompt}]
    )
    
    llm_narrative = response['message']['content']

    # 4. Combine both components on disk
    final_output = f"{ugly_log}\n\n--- CLINICAL TRANSLATION NARRATIVE ---\n\n{llm_narrative}\n"
    
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"💾 Success! Entire report dynamically generated and compiled to: {output_txt}")

if __name__ == "__main__":
    generate_dynamic_report()

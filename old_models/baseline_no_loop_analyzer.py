import json
from typing import Optional
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

# 2. Input dialogue
dialogue = """
A: You never listen to anything I say.
B: That's ridiculous. I listen all the time.
A: You're doing it right now.
B: Because you're attacking me.
"""

# 3. Initialize local client (defaults to localhost:11434)
client = Client()

print("Analyzing dialogue with local Llama...")

# 4. Query the model with a strict JSON schema
response = client.chat(
    model="llama3.2", # Swap to your specific local model tag if different (e.g., llama3.2, mistral)
    messages=[
        {
            "role": "system",
            "content": "You are an expert relationship counselor. Analyze the conversation and extract Gottman communication markers."
        },
        {
            "role": "user",
            "content": f"Analyze this dialogue:\n{dialogue}"
        }
    ],
    # This forces the local model to match your Pydantic structure exactly
    format=RelationshipAnalysis.model_json_schema()
)

# 5. Parse and print the validated result
raw_content = response['message']['content']
parsed_json = json.loads(raw_content)

print(json.dumps(parsed_json, indent=2))

import requests
import json

# Set up Ollama endpoint & model
OLLAMA_ENDPOINT = 'http://localhost:11434/api/generate'
MODEL = 'llama3.2'

def get_llm_response(prompt):
    # Send request
    response = requests.post(
        OLLAMA_ENDPOINT,
        headers={'Content-Type': 'application/json'},
        json={
            'model': MODEL,
            'prompt': prompt,
            'temperature': 0.7, # Adjust the temperature for randomness
            'max_tokens': 50, # Adjust the max tokens for the response length
            # 'stream:': False # Set to true for streaming responses
        }
    )
    # Collecting data
    full_response = ""

    for line in response.iter_lines():
        if line:
            try:
                partial = json.loads(line.decode('utf-8'))
                full_response += partial.get('response', '')
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)

    # Print the full response
    return full_response
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"

def call_llm(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 600,   # ⬅️ LIMIT OUTPUT
            }
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"


def call_llm_stream(prompt: str):
    """
    Generator that yields partial text chunks as they arrive from Ollama.
    """
    with requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 350,
                "num_ctx": 4096,
            },
        },
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            data = json.loads(line.decode("utf-8"))

            if "response" in data:
                yield data["response"]

            if data.get("done"):
                break

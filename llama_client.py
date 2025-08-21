
import requests

def query_llm(prompt: str, model: str = "llama3.2:3b", max_tokens: int = 512) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": max_tokens
        }
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.json()["response"]
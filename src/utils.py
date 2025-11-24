import os
import json
import requests

import tiktoken
from neo4j import GraphDatabase

neo4j_driver = GraphDatabase.driver(
    os.environ.get("NEO4J_URI"),
    auth=(os.environ.get("NEO4J_USERNAME"), os.environ.get("NEO4J_PASSWORD")),
    notifications_min_severity="OFF"
)

# Ollama host (include protocol and port if needed, e.g. "http://localhost:11434")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")


def _ollama_post(path: str, payload: dict):
    url = f"{OLLAMA_HOST}{path}"
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    # Ollama may return streaming; this helper assumes non-streamed JSON responses
    return resp.json()


def chunk_text(text, chunk_size, overlap, split_on_whitespace_only=True):
    chunks = []
    index = 0

    while index < len(text):
        if split_on_whitespace_only:
            prev_whitespace = 0
            left_index = index - overlap
            while left_index >= 0:
                if text[left_index] == " ":
                    prev_whitespace = left_index
                    break
                left_index -= 1
            next_whitespace = text.find(" ", index + chunk_size)
            if next_whitespace == -1:
                next_whitespace = len(text)
            chunk = text[prev_whitespace:next_whitespace].strip()
            chunks.append(chunk)
            index = next_whitespace + 1
        else:
            start = max(0, index - overlap + 1)
            end = min(index + chunk_size + overlap, len(text))
            chunk = text[start:end].strip()
            chunks.append(chunk)
            index += chunk_size

    return chunks


def num_tokens_from_string(string: str, model: str = "gpt-4") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def embed(texts, model="text-embedding-3-small"):
    """
    Use Ollama's embeddings endpoint.
    texts: single string or list of strings
    Returns: list of embeddings (one per input)
    """
    payload = {"model": model, "input": texts}
    response = _ollama_post("/api/embeddings", payload)
    # Expecting response like {"data": [{"embedding": [...]}, ...]}
    data = response.get("data", [])
    return [item.get("embedding") for item in data]


def chat(messages, model="gpt-4o", temperature=0, config=None):
    """
    messages: list of dicts like {"role": "system"|"user"|"assistant", "content": "..."}
    Returns: string content of the model's reply (best-effort parsing of Ollama response)
    """
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if config:
        payload.update(config)
    response = _ollama_post("/api/generate", payload)

    # Try to extract common fields returned by Ollama
    # Prefer choices -> message.content (OpenAI-like), then text, then results
    if isinstance(response, dict):
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            msg = choice.get("message") or {}
            content = msg.get("content")
            if content:
                return content
        if "text" in response:
            return response["text"]
        if "results" in response and len(response["results"]) > 0:
            # results may contain "content" or "text"
            res0 = response["results"][0]
            if isinstance(res0, dict):
                if "content" in res0:
                    return res0["content"]
                if "text" in res0:
                    return res0["text"]

    # Fallback: return JSON string
    return json.dumps(response)


def tool_choice(messages, model="gpt-4o", temperature=0, tools=None, config=None):
    """
    Similar to chat but returns tool call information if present.
    Ollama doesn't have an exact 'tools' API like some hosted LLMs; this is best-effort.
    """
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if tools:
        payload["tools"] = tools
    if config:
        payload.update(config)

    response = _ollama_post("/api/generate", payload)

    # Try to locate tool call info in the response
    if isinstance(response, dict):
        # OpenAI-like structure
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            msg = choice.get("message") or {}
            if "tool_calls" in msg:
                return msg["tool_calls"]
            if "tool_call" in msg:
                return msg["tool_call"]
        # Other structures
        if "tool_calls" in response:
            return response["tool_calls"]
        if "tool_call" in response:
            return response["tool_call"]

    # No tool info found; return full response for inspection
    return response


if __name__ == "__main__":
    # Print available Ollama models
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/models")
        resp.raise_for_status()
        print(resp.json())
    except Exception as e:
        print("Failed to list Ollama models:", e)
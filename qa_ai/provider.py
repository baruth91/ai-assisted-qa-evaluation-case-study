"""Ollama adapter; the model receives requirements but never evaluation labels."""

import json
from urllib.parse import urlparse

import requests


def client(base_url):
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("This teaching adapter accepts only a loopback HTTP Ollama server")
    session = requests.Session()
    session.trust_env = False
    return session


def model_metadata(session, base_url, config):
    response = session.get(base_url + "/api/version", timeout=10)
    response.raise_for_status()
    version = response.json()["version"]
    response = session.get(base_url + "/api/tags", timeout=10)
    response.raise_for_status()
    models = response.json()["models"]
    selected = next((model for model in models if model["name"] == config["model"]), None)
    if selected is None:
        raise ValueError("Configured model is not installed; see the README")
    if selected["digest"] != config["expected_digest"]:
        raise ValueError("Model digest changed; review and version the model config before running")
    return {
        "provider": "ollama",
        "runtime_version": version,
        "model": config["model"],
        "model_digest": selected["digest"],
    }


def generate(session, base_url, config, prompt, case, schema):
    user_data = {
        "requirements": case["requirements"],
        "acceptance_criteria": case["acceptance_criteria"],
    }
    response = session.post(
        base_url + "/api/chat",
        json={
            "model": config["model"],
            "stream": False,
            "format": schema,
            "options": config["options"],
            "keep_alive": "5m",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(user_data)},
            ],
        },
        timeout=(10, 300),
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("done"):
        raise ValueError("Model response did not complete")
    return {
        "raw_output": payload["message"]["content"],
        "done_reason": payload.get("done_reason"),
        "prompt_tokens": payload.get("prompt_eval_count"),
        "completion_tokens": payload.get("eval_count"),
        "duration_ns": payload.get("total_duration"),
    }

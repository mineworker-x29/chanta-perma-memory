from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
INPUT_PATH = PROJECT_ROOT / "scripts" / "output" / "memory_candidates.json"
OUTPUT_PATH = PROJECT_ROOT / "scripts" / "output" / "memory_candidates_refined.json"


@dataclass
class AppConfig:
    ollama_base_url: str
    ollama_model: str
    memory_refine_limit: int


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file does not exist: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    return AppConfig(
        ollama_base_url=str(raw["ollama_base_url"]).rstrip("/"),
        ollama_model=str(raw["ollama_model"]),
        memory_refine_limit=int(raw.get("memory_refine_limit", 10)),
    )


def load_memory_candidates(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Memory candidate file does not exist: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def build_prompt(candidate: dict[str, Any]) -> str:
    source_name = candidate.get("source_name", "")
    related_domain = candidate.get("related_domain", None)
    content = candidate.get("content", "")
    tags = safe_list(candidate.get("tags"))
    confidence = candidate.get("confidence", None)
    reason = candidate.get("reason", "")

    tag_str = ", ".join(tags) if tags else "(none)"

    return f"""
You are assisting ChantaPermaMemory.

Your task is to refine a provisional memory candidate conservatively.
Do not invent facts that are not present in the candidate.
Do not add new domains unless strongly implied by the existing fields.
If confidence is weak, keep it conservative.

Return JSON only with the following keys:
- refined_content
- refined_reason
- refined_confidence

Allowed refined_confidence values:
- low
- medium
- high

Candidate:
source_name: {source_name}
related_domain: {related_domain}
content: {content}
tags: {tag_str}
confidence: {confidence}
reason: {reason}
""".strip()


def call_ollama(base_url: str, model: str, prompt: str) -> str:
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    response = requests.post(url, json=payload, timeout=300)
    response.raise_for_status()
    data = response.json()

    return str(data.get("response", "")).strip()


def refine_candidate(candidate: dict[str, Any], config: AppConfig) -> dict[str, Any]:
    prompt = build_prompt(candidate)
    raw_response = call_ollama(config.ollama_base_url, config.ollama_model, prompt)

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        parsed = {
            "refined_content": candidate.get("content", ""),
            "refined_reason": f"LLM refinement failed to return valid JSON. Raw response: {raw_response[:300]}",
            "refined_confidence": candidate.get("confidence", "low") or "low",
        }

    refined = dict(candidate)
    refined["refined_content"] = parsed.get("refined_content", candidate.get("content", ""))
    refined["refined_reason"] = parsed.get("refined_reason", candidate.get("reason", ""))
    refined["refined_confidence"] = parsed.get("refined_confidence", candidate.get("confidence", "low") or "low")
    refined["refined_at"] = datetime.now(timezone.utc).isoformat()
    refined["refinement_model"] = config.ollama_model

    return refined


def build_refined_payload(source_payload: dict[str, Any], refined_candidates: list[dict[str, Any]], config: AppConfig) -> dict[str, Any]:
    return {
        "memory_version": "0.9",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_memory_version": source_payload.get("memory_version", "unknown"),
        "source_candidate_count": source_payload.get("candidate_count", 0),
        "refined_candidate_count": len(refined_candidates),
        "refinement_backend": "ollama",
        "refinement_model": config.ollama_model,
        "candidates": refined_candidates,
    }


def save_output(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main() -> None:
    config = load_config(CONFIG_PATH)
    source_payload = load_memory_candidates(INPUT_PATH)
    candidates = safe_list(source_payload.get("candidates"))

    limited_candidates = candidates[: config.memory_refine_limit]

    refined_candidates: list[dict[str, Any]] = []
    for idx, candidate in enumerate(limited_candidates, start=1):
        print(f"[INFO] Refining candidate {idx}/{len(limited_candidates)}: {candidate.get('memory_id')}")
        refined = refine_candidate(candidate, config)
        refined_candidates.append(refined)

    payload = build_refined_payload(source_payload, refined_candidates, config)
    save_output(payload, OUTPUT_PATH)

    print("[OK] Memory candidate refinement complete")
    print(f" - Input path   : {INPUT_PATH}")
    print(f" - Output path  : {OUTPUT_PATH}")
    print(f" - Model        : {config.ollama_model}")
    print(f" - Candidate cnt: {len(refined_candidates)}")


if __name__ == "__main__":
    main()
"""
Inference Script — AIPlatformEnv
=================================

Runs a baseline LLM agent against all three AIPlatformEnv tasks and emits
structured stdout logs in the mandatory [START] / [STEP] / [END] format.

Environment variables (required before submission):
    HF_TOKEN        Your Hugging Face / API key
    API_BASE_URL    LLM endpoint  (default: https://router.huggingface.co/v1)
    MODEL_NAME      Model identifier (default: Qwen/Qwen2.5-72B-Instruct)
    API_URL         AIPlatformEnv server base URL (default: http://localhost:8000)

Usage:
    python inference.py
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
import traceback
from typing import List, Optional

import httpx
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY: str = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or ""
API_BASE_URL: str = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_BASE_URL: str = os.getenv("API_URL", "http://localhost:8000")

BENCHMARK = "aiplatformenv"
MAX_STEPS = 3          # multi-step episodes
TEMPERATURE = 0.2
MAX_TOKENS = 300
SUCCESS_SCORE_THRESHOLD = 0.5

TASKS = ["answer_selection", "ranking_subtle", "ambiguity_calibration"]

# ---------------------------------------------------------------------------
# OpenAI client
# ---------------------------------------------------------------------------

client = OpenAI(api_key=API_KEY or "dummy", base_url=API_BASE_URL)

# ---------------------------------------------------------------------------
# Environment HTTP helpers
# ---------------------------------------------------------------------------

def env_reset(task_name: str) -> dict:
    resp = httpx.post(
        f"{ENV_BASE_URL}/reset",
        json={"task_name": task_name},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_step(action_payload: dict) -> dict:
    resp = httpx.post(
        f"{ENV_BASE_URL}/step",
        json=action_payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Agent prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert AI evaluator holding a multi-step conversation.
    Optional: If you need a hint, respond with:
    {"action_type": "search"}
    
    If you are ready to answer, respond with:
    {"action_type": "answer", "selected_index": <int>, "confidence": <float>, "reasoning": "..."}
""").strip()


def build_user_prompt(obs: dict) -> str:
    question = obs["question"]
    candidates = obs["candidate_responses"]
    hint = obs.get("hint", None)
    step = obs.get("step", 0)

    lines = [f"Question: {question}", ""]
    if hint:
        lines.append(f"--- HINT RECEIVED ---\n{hint}\n---------------------\n")
        
    lines.append("Candidate responses:")
    for i, c in enumerate(candidates):
        lines.append(f"  [{i}] {c}")
    lines.append("")
    
    if step == 0:
        lines.append("Instruction: You MUST execute a search action to gather more information. Respond ONLY with: {\"action_type\": \"search\"}")
    else:
        lines.append("Instruction: Now provide your final answer. Respond ONLY with: {\"action_type\": \"answer\", \"selected_index\": <int>, \"confidence\": <float>, \"reasoning\": \"<str>\"}")
    return "\n".join(lines)


def call_llm(prompt: str) -> dict:
    """Call the LLM and parse JSON response. Returns action dict."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    raw = response.choices[0].message.content.strip()

    # Try to extract JSON even if wrapped in markdown
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # fallback
        return {"action_type": "answer", "selected_index": 0, "confidence": 0.5, "reasoning": raw}


# ---------------------------------------------------------------------------
# Run a single task episode
# ---------------------------------------------------------------------------

def run_task(task_name: str) -> float:
    """Run one episode for a task and return the final score."""
    rewards: List[float] = []
    final_score = 0.0
    step_num = 0
    last_error: Optional[str] = None

    try:
        obs = env_reset(task_name)

        print(
            f"[START] task={task_name} env={BENCHMARK} model={MODEL_NAME}",
            flush=True,
        )

        done = obs.get("done", False)

        while not done and step_num < MAX_STEPS:
            step_num += 1
            action_str = "null"
            reward = 0.0
            last_error = None

            try:
                user_prompt = build_user_prompt(obs)
                llm_out = call_llm(user_prompt)

                action_type = llm_out.get("action_type", "answer")
                selected_index = llm_out.get("selected_index", 0)
                confidence = float(llm_out.get("confidence", 0.5))
                reasoning = str(llm_out.get("reasoning", ""))
                confidence = max(0.0, min(1.0, confidence))

                if action_type == "search":
                    action_str = "search()"
                    action_payload = {"action_type": "search"}
                else:
                    action_str = f"answer(index={selected_index}, conf={confidence:.2f})"
                    action_payload = {
                        "action_type": "answer",
                        "selected_index": selected_index,
                        "confidence": confidence,
                        "reasoning": reasoning,
                    }

                result = env_step(action_payload)
                reward = float(result["reward"])
                done = bool(result["done"])
                obs = result["observation"]
                if done:
                    final_score = reward

            except Exception as e:
                last_error = str(e)
                done = True

            rewards.append(reward)
            print(
                f"[STEP] step={step_num} action={action_str} "
                f"reward={reward:.2f} done={str(done).lower()} "
                f"error={last_error if last_error else 'null'}",
                flush=True,
            )

    except Exception as e:
        last_error = str(e)
        if step_num == 0:
            step_num = 1
            rewards = [0.0]
            print(
                f"[START] task={task_name} env={BENCHMARK} model={MODEL_NAME}",
                flush=True,
            )
            print(
                f"[STEP] step=1 action=null reward=0.00 done=true error={last_error}",
                flush=True,
            )

    success = final_score >= SUCCESS_SCORE_THRESHOLD
    rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"

    print(
        f"[END] success={str(success).lower()} steps={step_num} "
        f"score={final_score:.2f} rewards={rewards_str}",
        flush=True,
    )

    return final_score


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    total_score = 0.0
    results = {}

    for task in TASKS:
        print(f"\n{'='*60}", flush=True)
        print(f"Running task: {task}", flush=True)
        print(f"{'='*60}", flush=True)
        score = run_task(task)
        results[task] = score
        total_score += score

    avg = total_score / len(TASKS)

    print(f"\n{'='*60}", flush=True)
    print("FINAL RESULTS:", flush=True)
    for task, score in results.items():
        print(f"  {task}: {score:.4f}", flush=True)
    print(f"  Average: {avg:.4f}", flush=True)
    print(f"{'='*60}", flush=True)


if __name__ == "__main__":
    main()

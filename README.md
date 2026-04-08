---
title: AIPlatformEnv
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---
# AIPlatformEnv 🤖

> **An OpenEnv environment where AI agents learn to evaluate AI-generated responses.**

[![openenv](https://img.shields.io/badge/openenv-compatible-blue)](https://github.com/meta-pytorch/OpenEnv)

---

## Overview

**AIPlatformEnv** simulates a real-world AI workflow: given a question and a set of candidate responses, an agent must:

1. **Select** the best / most correct response
2. **Provide** a calibrated confidence score

This mirrors practical tasks like LLM output evaluation, RAG pipeline quality control, and prompt engineering — making it highly relevant for training and benchmarking next-generation agents.

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `question` | `str` | The question or problem to reason about |
| `candidate_responses` | `List[str]` | 4 candidate answers to evaluate |
| `metadata` | `dict` | Task name, difficulty, domain, episode ID |
| `step` | `int` | Current step number |
| `done` | `bool` | Whether the episode has ended |
| `last_reward` | `float` | Reward from the last action |

---

## Action Space

| Field | Type | Description |
|---|---|---|
| `selected_index` | `int` | 0-based index of chosen candidate |
| `confidence` | `float [0,1]` | Agent's confidence in the selection |
| `reasoning` | `str` (optional) | Free-text explanation (not graded) |

---

## Tasks

### Task 1 — Answer Selection (`easy`)
Clear factual questions with one correct answer and obvious distractors.
**Score = 0.7 × correctness + 0.3 × calibration**

### Task 2 — Ranking Subtle Differences (`medium`)
Multiple plausible AI responses; differences lie in depth, accuracy, and completeness.
**Score = 0.5 × correctness + 0.3 × ranking_quality + 0.2 × calibration**

### Task 3 — Ambiguity & Calibration (`hard`)
All candidates are partially correct. Requires careful reasoning + well-calibrated confidence. Overconfidence is penalized.
**Score = 0.4 × correctness + 0.3 × ranking_quality + 0.3 × calibration**

---

## Reward Function

Rewards are dense and per-step (though episodes are single-step):

```python
reward = w1 * correctness + w2 * ranking_quality + w3 * calibration
```

- **Correctness**: 1.0 if correct index selected, else 0.0  
- **Ranking quality**: partial credit based on how good the selected option is  
- **Calibration**: `1 - |confidence - correctness|` — rewards well-calibrated uncertainty

---

## Environment API

```python
# Reset episode
POST /reset   body: {"task_name": "answer_selection"}  → Observation

# Take a step
POST /step    body: {"selected_index": 2, "confidence": 0.85}  → {observation, reward, done, info}

# Get state
GET  /state   → AIPlatformState

# List tasks
GET  /tasks   → [{name, difficulty, description}, ...]

# Health
GET  /health  → {"status": "ok"}
```

---

## Setup & Usage

### Run locally

```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Run with Docker

```bash
docker build -t aiplatformenv .
docker run -p 8000:8000 aiplatformenv
```

### Run inference baseline

```bash
export HF_TOKEN=your_token
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export API_URL=http://localhost:8000

python inference.py
```

---

## Baseline Scores

| Task | Difficulty | Baseline Score |
|---|---|---|
| answer_selection | easy | ~0.85 |
| ranking_subtle | medium | ~0.65 |
| ambiguity_calibration | hard | ~0.45 |

---

## Project Structure

```
aiplatformenv/
├── models.py        # Pydantic models: Observation, Action, State, Reward
├── data.py          # Question bank (5 questions × 3 tasks)
├── tasks.py         # Graders for each task
├── env.py           # Core environment: reset(), step(), state
├── server.py        # FastAPI HTTP server
├── inference.py     # Baseline inference script (OpenAI client)
├── openenv.yaml     # OpenEnv manifest
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Evaluation Criteria Coverage

| Criterion | Weight | How we address it |
|---|---|---|
| Real-world utility | 30% | Models LLM evaluation / RAG QC workflows |
| Task & grader quality | 25% | 3 tasks easy→hard, deterministic graders |
| Environment design | 20% | Clean state, partial credit rewards |
| Code quality & spec | 15% | Typed models, openenv.yaml, Dockerfile |
| Creativity & novelty | 10% | AI evaluating AI, calibration task |

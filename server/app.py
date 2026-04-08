"""
AIPlatformEnv — FastAPI server exposing the environment over HTTP.

Endpoints:
    POST /reset          → initial observation
    POST /step           → (observation, reward, done, info)
    GET  /state          → current episode state
    GET  /tasks          → list of available tasks
    GET  /health         → liveness check
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import AIPlatformAction, AIPlatformObservation, AIPlatformState
from env import AIPlatformEnv
from tasks import TASK_METADATA

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ResetRequest(BaseModel):
    task_name: Optional[str] = None
    seed: Optional[int] = None


class StepRequest(BaseModel):
    selected_index: int
    confidence: float
    reasoning: Optional[str] = None


class StepResponse(BaseModel):
    observation: AIPlatformObservation
    reward: float
    done: bool
    info: Dict[str, Any]


class TasksResponse(BaseModel):
    tasks: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AIPlatformEnv",
    description=(
        "An OpenEnv environment where an AI agent evaluates AI-generated responses. "
        "Three tasks with increasing difficulty: answer selection (easy), "
        "ranking subtle differences (medium), and ambiguity + calibration (hard)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance (single-user; for multi-user extend with session management)
_env: Optional[AIPlatformEnv] = None


def _get_env() -> AIPlatformEnv:
    global _env
    if _env is None:
        _env = AIPlatformEnv()
    return _env


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "env": "AIPlatformEnv", "version": "1.0.0"}


@app.post("/reset", response_model=AIPlatformObservation)
def reset(req: ResetRequest = ResetRequest()):
    global _env
    seed = req.seed
    task = req.task_name
    _env = AIPlatformEnv(task_name=task, seed=seed)
    try:
        obs = _env.reset(task_name=task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return obs


@app.post("/step", response_model=StepResponse)
def step(req: StepRequest):
    env = _get_env()
    action = AIPlatformAction(
        selected_index=req.selected_index,
        confidence=req.confidence,
        reasoning=req.reasoning,
    )
    try:
        obs, reward, done, info = env.step(action)
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StepResponse(observation=obs, reward=reward, done=done, info=info)


@app.get("/state", response_model=AIPlatformState)
def state():
    env = _get_env()
    return env.state


@app.get("/tasks", response_model=TasksResponse)
def tasks():
    return TasksResponse(tasks=list(TASK_METADATA.values()))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

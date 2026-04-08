"""
AIPlatformEnv — Typed Pydantic models for Observation, Action, State, and Reward.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Observation
# ---------------------------------------------------------------------------

class AIPlatformObservation(BaseModel):
    """What the agent sees at each step."""

    question: str = Field(description="The question or problem the agent must reason about.")
    candidate_responses: List[str] = Field(
        description="List of candidate responses. The agent must pick the best one."
    )
    correct_index: Optional[int] = Field(
        default=None,
        description="Ground-truth index (exposed only after episode ends, None during play)."
    )
    hint: Optional[str] = Field(
        default=None,
        description="Optional hint provided if the agent invokes the search action."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra info: task name, difficulty, domain.",
    )
    step: int = Field(default=0, description="Current step number in the episode.")
    done: bool = Field(default=False, description="Whether the episode is over.")
    last_reward: float = Field(default=0.0, description="Reward from the last action.")


# ---------------------------------------------------------------------------
# Action
# ---------------------------------------------------------------------------

class AIPlatformAction(BaseModel):
    """What the agent submits each step."""

    action_type: str = Field(
        default="answer",
        description="Must be 'answer' or 'search'. Search fetches a hint without ending the episode."
    )
    selected_index: Optional[int] = Field(
        default=None,
        description="Zero-based index into candidate_responses. Required if action_type == 'answer'."
    )
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Agent confidence in its selection. Required if action_type == 'answer'."
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional free-text reasoning. Not used in grading but logged."
    )


# ---------------------------------------------------------------------------
# State  (internal — also surfaced via /state endpoint)
# ---------------------------------------------------------------------------

class AIPlatformState(BaseModel):
    """Internal episode state."""

    task_name: str = Field(description="Active task identifier.")
    episode_id: str = Field(description="Unique episode UUID.")
    step_count: int = Field(default=0)
    max_steps: int = Field(default=3, description="Max steps per episode.")
    cumulative_reward: float = Field(default=0.0)
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Log of (action, reward) pairs taken so far.",
    )
    done: bool = Field(default=False)


# ---------------------------------------------------------------------------
# Reward
# ---------------------------------------------------------------------------

class AIPlatformReward(BaseModel):
    """Breakdown of the reward signal."""

    total: float = Field(description="Overall reward in [0.0, 1.0].")
    correctness: float = Field(description="Was the correct candidate selected? 0 or 1.")
    ranking_quality: float = Field(
        description="Partial credit for selecting a near-correct candidate."
    )
    calibration: float = Field(
        description="How well the confidence score matched actual correctness."
    )

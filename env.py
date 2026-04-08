"""
AIPlatformEnv — Core environment class implementing the OpenEnv interface.

API:
    reset(task_name=None)  → AIPlatformObservation
    step(action)           → (AIPlatformObservation, float, bool, dict)
    state                  → AIPlatformState
"""
from __future__ import annotations

import random
import uuid
from typing import Any, Dict, List, Optional, Tuple

from models import AIPlatformAction, AIPlatformObservation, AIPlatformReward, AIPlatformState
from data import TASK_DATA, TASK_NAMES
from tasks import GRADERS, TASK_METADATA


class AIPlatformEnv:
    """
    OpenEnv-compatible environment for evaluating AI response quality.

    An episode consists of a single question presented to the agent.
    The agent selects one of the candidate responses and provides a confidence score.
    The grader evaluates the action and returns a structured reward.
    """

    def __init__(self, task_name: Optional[str] = None, seed: Optional[int] = None):
        self._task_name: str = task_name or TASK_NAMES[0]
        self._seed = seed
        self._rng = random.Random(seed)
        self._state: Optional[AIPlatformState] = None
        self._current_item: Optional[Dict[str, Any]] = None
        self._validate_task(self._task_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self, task_name: Optional[str] = None) -> AIPlatformObservation:
        """Start a new episode. Returns the first (and only) observation."""
        if task_name:
            self._validate_task(task_name)
            self._task_name = task_name

        episode_id = str(uuid.uuid4())
        items = TASK_DATA[self._task_name]
        self._current_item = self._rng.choice(items)

        meta = TASK_METADATA[self._task_name]
        self._state = AIPlatformState(
            task_name=self._task_name,
            episode_id=episode_id,
            step_count=0,
            max_steps=meta["max_steps"],
            cumulative_reward=0.0,
            history=[],
            done=False,
        )

        return self._build_observation(done=False, last_reward=0.0)

    def step(self, action: AIPlatformAction) -> Tuple[AIPlatformObservation, float, bool, Dict]:
        """Execute one action. Returns (observation, reward, done, info)."""
        if self._state is None or self._current_item is None:
            raise RuntimeError("Call reset() before step().")
        if self._state.done:
            raise RuntimeError("Episode is already done. Call reset() to start a new one.")

        # Tool Use: Search
        if action.action_type == "search":
            self._state.step_count += 1
            self._state.history.append({
                "step": self._state.step_count,
                "action_type": "search",
            })
            obs = self._build_observation(done=False, last_reward=0.0)
            obs.hint = self._current_item.get("hint", "No hint available.")
            
            return obs, 0.0, False, {}

        # Answer logic
        n_candidates = len(self._current_item["candidates"])
        if action.selected_index is None or not (0 <= action.selected_index < n_candidates):
            raise ValueError(
                f"selected_index {action.selected_index} invalid for action_type='answer'."
            )
        if action.confidence is None:
            raise ValueError("confidence must be provided for action_type='answer'.")

        # Grade
        grader = GRADERS[self._task_name]
        grade = grader.grade(
            action_selected=action.selected_index,
            action_confidence=action.confidence,
            item=self._current_item,
        )

        # Update state
        self._state.step_count += 1
        self._state.cumulative_reward += grade.score
        self._state.done = True  # single-step episodes
        self._state.history.append(
            {
                "step": self._state.step_count,
                "action_type": "answer",
                "selected_index": action.selected_index,
                "confidence": action.confidence,
                "reasoning": action.reasoning,
                "reward": grade.score,
                "correctness": grade.correctness,
                "ranking_quality": grade.ranking_quality,
                "calibration": grade.calibration,
                "correct_index": self._current_item["correct_index"],
            }
        )

        obs = self._build_observation(done=True, last_reward=grade.score)
        # Reveal correct answer after episode ends
        obs.correct_index = self._current_item["correct_index"]

        info = {
            "episode_id": self._state.episode_id,
            "task_name": self._task_name,
            "difficulty": self._current_item["difficulty"],
            "correctness": grade.correctness,
            "ranking_quality": grade.ranking_quality,
            "calibration": grade.calibration,
            "correct_index": self._current_item["correct_index"],
        }

        return obs, grade.score, True, info

    @property
    def state(self) -> AIPlatformState:
        """Return current episode state (or empty state if no episode started)."""
        if self._state is None:
            return AIPlatformState(
                task_name=self._task_name,
                episode_id="",
                step_count=0,
                max_steps=1,
                cumulative_reward=0.0,
                history=[],
                done=False,
            )
        return self._state

    def close(self) -> None:
        """No-op cleanup (provided for API symmetry)."""
        pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_observation(self, done: bool, last_reward: float) -> AIPlatformObservation:
        assert self._current_item is not None
        assert self._state is not None
        return AIPlatformObservation(
            question=self._current_item["question"],
            candidate_responses=self._current_item["candidates"],
            metadata={
                "task_name": self._task_name,
                "difficulty": self._current_item["difficulty"],
                "domain": self._current_item["domain"],
                "episode_id": self._state.episode_id,
            },
            step=self._state.step_count,
            done=done,
            last_reward=last_reward,
        )

    @staticmethod
    def _validate_task(task_name: str) -> None:
        if task_name not in TASK_DATA:
            raise ValueError(
                f"Unknown task '{task_name}'. Valid tasks: {TASK_NAMES}"
            )

    # ------------------------------------------------------------------
    # Class-level info
    # ------------------------------------------------------------------

    @classmethod
    def available_tasks(cls) -> List[str]:
        return TASK_NAMES

    @classmethod
    def task_info(cls, task_name: str) -> Dict[str, Any]:
        cls._validate_task(task_name)  # type: ignore[arg-type]
        return TASK_METADATA[task_name]

"""
AIPlatformEnv — Task definitions and deterministic graders.

Each grader returns a score in [0.0, 1.0].
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class GradeResult:
    score: float          # overall [0.0, 1.0]
    correctness: float    # binary 0 or 1
    ranking_quality: float   # partial positional credit
    calibration: float    # confidence calibration quality


# ---------------------------------------------------------------------------
# Shared grading helpers
# ---------------------------------------------------------------------------

def _correctness(selected: int, correct: int) -> float:
    return 1.0 if selected == correct else 0.0


def _ranking_quality(selected: int, quality_ranking: list[int]) -> float:
    """Partial credit based on position in quality_ranking (best → worst).

    Position 0  → 1.0
    Position 1  → 0.6
    Position 2  → 0.3
    Position 3+ → 0.0
    """
    position_scores = {0: 1.0, 1: 0.6, 2: 0.3}
    try:
        pos = quality_ranking.index(selected)
    except ValueError:
        pos = len(quality_ranking)
    return position_scores.get(pos, 0.0)


def _calibration(confidence: float, correctness: float) -> float:
    """Score how well confidence matches actual correctness (Brier-style).

    Returns 1 - |confidence - correctness| so:
      • Perfect calibration (confidence == correctness) → 1.0
      • Worst case (confident but wrong, or unconfident but right) → 0.0
    """
    return 1.0 - abs(confidence - correctness)


# ---------------------------------------------------------------------------
# Task 1 — Easy: Answer Selection
# ---------------------------------------------------------------------------

class AnswerSelectionGrader:
    """
    Single correct answer among obvious distractors.
    Score = 0.7 * correctness + 0.3 * calibration
    """
    TASK_NAME = "answer_selection"
    DIFFICULTY = "easy"

    def grade(self, action_selected: int, action_confidence: float,
              item: Dict[str, Any]) -> GradeResult:
        c = _correctness(action_selected, item["correct_index"])
        rq = _ranking_quality(action_selected, item["quality_ranking"])
        cal = _calibration(action_confidence, c)

        raw = 0.7 * c + 0.3 * cal
        score = round(max(0.01, min(0.99, raw)), 4)
        return GradeResult(score=score, correctness=c, ranking_quality=rq, calibration=cal)


# ---------------------------------------------------------------------------
# Task 2 — Medium: Ranking Subtle Differences
# ---------------------------------------------------------------------------

class RankingSubtleGrader:
    """
    Multiple plausible responses; agent must identify the best.
    Score = 0.5 * correctness + 0.3 * ranking_quality + 0.2 * calibration
    """
    TASK_NAME = "ranking_subtle"
    DIFFICULTY = "medium"

    def grade(self, action_selected: int, action_confidence: float,
              item: Dict[str, Any]) -> GradeResult:
        c = _correctness(action_selected, item["correct_index"])
        rq = _ranking_quality(action_selected, item["quality_ranking"])
        cal = _calibration(action_confidence, c)

        raw = 0.5 * c + 0.3 * rq + 0.2 * cal
        score = round(max(0.01, min(0.99, raw)), 4)
        return GradeResult(score=score, correctness=c, ranking_quality=rq, calibration=cal)


# ---------------------------------------------------------------------------
# Task 3 — Hard: Ambiguity + Calibration
# ---------------------------------------------------------------------------

class AmbiguityCalibrationGrader:
    """
    All responses partially correct; agent must pick the best AND be calibrated.
    Score = 0.4 * correctness + 0.3 * ranking_quality + 0.3 * calibration
    Confidence weight is highest here — reward proportional penalty for overconfidence.
    """
    TASK_NAME = "ambiguity_calibration"
    DIFFICULTY = "hard"

    def grade(self, action_selected: int, action_confidence: float,
              item: Dict[str, Any]) -> GradeResult:
        c = _correctness(action_selected, item["correct_index"])
        rq = _ranking_quality(action_selected, item["quality_ranking"])
        cal = _calibration(action_confidence, c)

        # Extra penalty: if confident but wrong, score is cut further
        overconfidence_penalty = 0.0
        if c == 0.0 and action_confidence > 0.7:
            overconfidence_penalty = 0.1 * (action_confidence - 0.7)

        raw = 0.4 * c + 0.3 * rq + 0.3 * cal - overconfidence_penalty
        score = round(max(0.01, min(0.99, raw)), 4)
        return GradeResult(score=score, correctness=c, ranking_quality=rq, calibration=cal)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

GRADERS = {
    AnswerSelectionGrader.TASK_NAME: AnswerSelectionGrader(),
    RankingSubtleGrader.TASK_NAME: RankingSubtleGrader(),
    AmbiguityCalibrationGrader.TASK_NAME: AmbiguityCalibrationGrader(),
}

TASK_METADATA = {
    "answer_selection": {
        "name": "answer_selection",
        "display_name": "Answer Selection",
        "difficulty": "easy",
        "description": (
            "The agent must identify the single correct answer among obvious distractors. "
            "Graded on correctness and confidence calibration."
        ),
        "max_steps": 1,
    },
    "ranking_subtle": {
        "name": "ranking_subtle",
        "display_name": "Ranking Subtle Differences",
        "difficulty": "medium",
        "description": (
            "Multiple plausible AI-generated responses. The agent must select the most accurate "
            "and complete answer. Graded on correctness, ranking quality, and calibration."
        ),
        "max_steps": 1,
    },
    "ambiguity_calibration": {
        "name": "ambiguity_calibration",
        "display_name": "Ambiguity & Calibration",
        "difficulty": "hard",
        "description": (
            "All candidates are partially correct. The agent must reason carefully to select "
            "the best answer AND provide a well-calibrated confidence score. Overconfidence is penalized."
        ),
        "max_steps": 1,
    },
}

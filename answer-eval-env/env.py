from typing import Tuple, Dict, Any, Optional
from models import AnswerInput
from grader import EvaluatorEngine
from tasks import get_task


class AnswerEvalEnv:
    """
    OpenEnv-compliant evaluation environment for grading student answers.

    Lifecycle:
        1. reset(question_id)  → loads a task and returns the initial state
        2. step(action)        → evaluates the student answer, returns (state, reward, done, info)
        3. state()             → returns the current state snapshot
    """

    def __init__(self):
        self.grader = EvaluatorEngine()
        self.current_state: Optional[Dict[str, Any]] = None

    # ── OpenEnv interface ────────────────────────────────────────────────────

    def reset(self, question_id: str) -> Tuple[Dict[str, Any], Dict]:
        """
        Reset environment with a specific task.
        Returns: (initial_state, info_dict)
        """
        task = get_task(question_id)
        if not task:
            raise ValueError(f"Task '{question_id}' not found.")

        self.current_state = {
            "question": task.text,
            "key_concepts": task.key_concepts,
            "difficulty": task.difficulty,
            "student_answer": None,
        }
        return self.current_state, {}

    def step(self, action: AnswerInput) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """
        Submit a student answer for evaluation.
        Returns: (next_state, reward, done, info)
          - reward is a float in [0.0, 1.0]
        """
        if self.current_state is None:
            raise RuntimeError("Environment must be reset() before calling step().")

        task = get_task(action.question_id)
        if not task:
            raise ValueError(f"Task '{action.question_id}' not found.")

        self.current_state["student_answer"] = action.student_answer

        eval_result = self.grader.evaluate(action.student_answer, task.key_concepts)

        # Reward = normalised score in [0.0, 1.0]
        reward: float = eval_result.score

        done = True   # single-step episode

        info = {
            "evaluation": eval_result.model_dump()
        }

        return self.current_state, reward, done, info

    def state(self) -> Dict[str, Any]:
        """
        Returns the current environment state.
        Raises RuntimeError if reset() has not been called yet.
        """
        if self.current_state is None:
            raise RuntimeError("No active state. Call reset() first.")
        return self.current_state

"""
inference.py — Baseline agent for Answer-Eval-Env
Runs all three difficulty tasks and prints evaluation logs in the required format.
"""
from env import AnswerEvalEnv
from models import AnswerInput

# ---------------------------------------------------------------------------
# Sample answers per difficulty
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "task_id": "easy_1",
        "student_answer": (
            "Photosynthesis is the process where plants use sunlight, water, and "
            "carbon dioxide to produce glucose and oxygen using chlorophyll."
        ),
    },
    {
        "task_id": "medium_1",
        "student_answer": (
            "A binary search tree organises nodes so that the left child is always "
            "less than the parent and the right child is greater than the parent. "
            "This structure allows search operations in O(log n) time."
        ),
    },
    {
        "task_id": "hard_1",
        "student_answer": (
            "I don't know much about quantum stuff, just that things are small."
        ),
    },
]


def format_feedback(feedback: dict) -> str:
    """Build a single-line human-readable feedback string."""
    parts = []
    if feedback.get("covered_concepts"):
        parts.append(f"Covered: {', '.join(feedback['covered_concepts'])}")
    if feedback.get("missing_concepts"):
        parts.append(f"Missing: {', '.join(feedback['missing_concepts'])}")
    if feedback.get("weak_areas") and feedback["weak_areas"] != "None":
        parts.append(feedback["weak_areas"])
    if feedback.get("suggestions"):
        parts.append(feedback["suggestions"])
    return " | ".join(parts) if parts else "No additional feedback."


def main():
    env = AnswerEvalEnv()

    for case in TEST_CASES:
        task_id = case["task_id"]
        student_answer = case["student_answer"]

        # Reset environment and get initial state
        state, _ = env.reset(task_id)
        question = state["question"]

        # Submit answer
        action = AnswerInput(question_id=task_id, student_answer=student_answer)
        _, reward, _, info = env.step(action)

        feedback_dict = info["evaluation"]["feedback"]
        feedback_text = format_feedback(feedback_dict)

        # ── Required log format ──────────────────────────────────────────────
        print("[START]")
        print(f"task_id: {task_id}")
        print(f"question: {question}")
        print()
        print("[STEP]")
        print(f"student_answer: {student_answer}")
        print(f"score: {reward:.4f}")
        print(f"feedback: {feedback_text}")
        print()
        print("[END]")
        print()


if __name__ == "__main__":
    main()

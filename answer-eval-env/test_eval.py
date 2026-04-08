"""
test_eval.py — Unit + integration tests for answer-eval-env
Run with: python -m pytest test_eval.py -v
"""
import pytest
from models import AnswerInput, EvaluationResult
from grader import EvaluatorEngine
from env import AnswerEvalEnv
from tasks import get_task, get_tasks
from utils.helpers import clean_text, similar, match_concepts


# ─── Helper / Utility Tests ────────────────────────────────────────────────────

class TestHelpers:
    def test_clean_text_lowercases(self):
        assert clean_text("Hello World") == "hello world"

    def test_clean_text_removes_punctuation(self):
        assert clean_text("photosynthesis, process!") == "photosynthesis process"

    def test_clean_text_empty(self):
        assert clean_text("") == ""

    def test_similar_identical(self):
        assert similar("hello", "hello") == 1.0

    def test_similar_completely_different(self):
        assert similar("abc", "xyz") < 0.5

    def test_match_concepts_all_covered(self):
        answer = "Plants use sunlight, water, and carbon dioxide to produce glucose and oxygen."
        concepts = ["sunlight", "water", "carbon dioxide", "glucose", "oxygen"]
        covered, missing = match_concepts(answer, concepts)
        assert len(covered) == 5
        assert len(missing) == 0

    def test_match_concepts_none_covered(self):
        answer = "I have no idea."
        concepts = ["sunlight", "photosynthesis"]
        covered, missing = match_concepts(answer, concepts)
        assert len(covered) == 0
        assert len(missing) == 2

    def test_match_concepts_fuzzy(self):
        # slight typo: "sunlite" vs "sunlight"
        answer = "photosinthesis uses sunlite"
        concepts = ["sunlight"]
        covered, missing = match_concepts(answer, concepts)
        assert "sunlight" in covered


# ─── Grader Tests ──────────────────────────────────────────────────────────────

class TestGrader:
    def setup_method(self):
        self.grader = EvaluatorEngine()

    def test_score_in_unit_range(self):
        """All scores must be in [0.0, 1.0]."""
        concepts = ["sunlight", "water", "carbon dioxide", "oxygen", "glucose"]
        answer = "Photosynthesis uses sunlight, water, and carbon dioxide to produce oxygen and glucose."
        result = self.grader.evaluate(answer, concepts)
        assert 0.0 <= result.score <= 1.0

    def test_perfect_answer_high_score(self):
        concepts = ["sunlight", "water", "carbon dioxide", "oxygen", "glucose"]
        answer = "Photosynthesis uses sunlight, water, and carbon dioxide to produce oxygen and glucose."
        result = self.grader.evaluate(answer, concepts)
        assert result.score >= 0.8

    def test_empty_answer_score_0(self):
        result = self.grader.evaluate("", ["sunlight", "water"])
        assert result.score == 0.0

    def test_very_short_answer_score_0(self):
        result = self.grader.evaluate("yes", ["photosynthesis"])
        assert result.score == 0.0

    def test_no_concepts_score_1(self):
        result = self.grader.evaluate("Any answer here", [])
        assert result.score == 1.0

    def test_partial_answer_partial_score(self):
        concepts = ["sunlight", "water", "carbon dioxide", "oxygen", "glucose"]
        answer = "Plants use sunlight and water."
        result = self.grader.evaluate(answer, concepts)
        assert 0.0 < result.score < 1.0

    def test_weak_areas_message_zero_score(self):
        result = self.grader.evaluate(
            "This is an unrelated long answer about nothing at all.",
            ["quantum", "entanglement"]
        )
        assert "fails to address" in result.feedback.weak_areas

    def test_weak_areas_message_partial_score(self):
        concepts = ["sunlight", "water", "carbon dioxide", "oxygen", "glucose"]
        answer = "Plants use sunlight only."
        result = self.grader.evaluate(answer, concepts)
        assert (
            "misses major" in result.feedback.weak_areas
            or "lacks completeness" in result.feedback.weak_areas
        )

    def test_feedback_covered_and_missing_populated(self):
        concepts = ["sunlight", "water", "glucose"]
        answer = "Plants use sunlight and water."
        result = self.grader.evaluate(answer, concepts)
        assert "sunlight" in result.feedback.covered_concepts
        assert "water" in result.feedback.covered_concepts
        assert "glucose" in result.feedback.missing_concepts

    def test_max_score_is_1(self):
        result = self.grader.evaluate("any answer text here", ["word"])
        assert result.max_score == 1.0


# ─── Task Registry Tests ───────────────────────────────────────────────────────

class TestTasks:
    def test_all_tasks_loaded(self):
        tasks = get_tasks()
        assert len(tasks) == 9  # 3 easy + 3 medium + 3 hard

    def test_at_least_one_easy(self):
        tasks = get_tasks()
        assert any(t.difficulty == "easy" for t in tasks)

    def test_at_least_one_medium(self):
        tasks = get_tasks()
        assert any(t.difficulty == "medium" for t in tasks)

    def test_at_least_one_hard(self):
        tasks = get_tasks()
        assert any(t.difficulty == "hard" for t in tasks)

    def test_get_task_easy(self):
        t = get_task("easy_1")
        assert t is not None
        assert t.difficulty == "easy"

    def test_get_task_medium(self):
        t = get_task("medium_1")
        assert t is not None
        assert t.difficulty == "medium"

    def test_get_task_hard(self):
        t = get_task("hard_1")
        assert t is not None
        assert t.difficulty == "hard"

    def test_get_task_invalid_returns_none(self):
        assert get_task("nonexistent_99") is None

    def test_all_tasks_have_key_concepts(self):
        for task in get_tasks():
            assert len(task.key_concepts) > 0, f"Task {task.id} has no key concepts"


# ─── Environment Lifecycle Tests ───────────────────────────────────────────────

class TestEnvironment:
    def setup_method(self):
        self.env = AnswerEvalEnv()

    def test_reset_returns_state(self):
        state, _ = self.env.reset("easy_1")
        assert "question" in state
        assert "key_concepts" in state
        assert "difficulty" in state
        assert state["student_answer"] is None

    def test_state_method_after_reset(self):
        self.env.reset("easy_1")
        s = self.env.state()
        assert s["question"] is not None

    def test_state_method_before_reset_raises(self):
        env = AnswerEvalEnv()
        with pytest.raises(RuntimeError):
            env.state()

    def test_reset_invalid_task_raises(self):
        with pytest.raises(ValueError):
            self.env.reset("bad_task_id")

    def test_step_without_reset_raises(self):
        env = AnswerEvalEnv()
        action = AnswerInput(question_id="easy_1", student_answer="some answer")
        with pytest.raises(RuntimeError):
            env.step(action)

    def test_step_returns_done_true(self):
        self.env.reset("easy_1")
        action = AnswerInput(question_id="easy_1", student_answer="sunlight water carbon dioxide")
        _, reward, done, info = self.env.step(action)
        assert done is True

    def test_step_reward_in_unit_range(self):
        self.env.reset("medium_1")
        action = AnswerInput(
            question_id="medium_1",
            student_answer=(
                "A BST has nodes where left child is less than parent and "
                "right child is greater than parent with log n complexity."
            )
        )
        _, reward, done, info = self.env.step(action)
        assert 0.0 <= reward <= 1.0

    def test_step_info_has_evaluation(self):
        self.env.reset("hard_1")
        action = AnswerInput(
            question_id="hard_1",
            student_answer="Quantum entanglement links particles across distance."
        )
        _, _, _, info = self.env.step(action)
        assert "evaluation" in info
        assert "score" in info["evaluation"]
        assert "feedback" in info["evaluation"]


# ─── End-to-End Score Banding Tests ────────────────────────────────────────────

class TestEndToEnd:
    def setup_method(self):
        self.env = AnswerEvalEnv()

    def test_good_answer_high_score(self):
        """Good answer → score in [0.8, 1.0]"""
        self.env.reset("easy_1")
        action = AnswerInput(
            question_id="easy_1",
            student_answer=(
                "Photosynthesis is the process where plants absorb sunlight, water, "
                "and carbon dioxide using chlorophyll to produce glucose and oxygen."
            )
        )
        _, reward, _, _ = self.env.step(action)
        assert reward >= 0.8, f"Expected >= 0.8 but got {reward}"

    def test_partial_answer_medium_score(self):
        """Partial answer → score in [0.3, 0.75]"""
        self.env.reset("medium_1")
        action = AnswerInput(
            question_id="medium_1",
            student_answer="Binary trees have nodes and left and right children."
        )
        _, reward, _, _ = self.env.step(action)
        assert 0.3 <= reward <= 0.75, f"Expected 0.3–0.75 but got {reward}"

    def test_bad_answer_low_score(self):
        """Weak/off-topic answer → score in [0.0, 0.3]"""
        self.env.reset("hard_1")
        action = AnswerInput(
            question_id="hard_1",
            student_answer="I don't know much about quantum stuff, just that things are small."
        )
        _, reward, _, _ = self.env.step(action)
        assert reward < 0.3, f"Expected < 0.3 but got {reward}"

    def test_misleading_confident_answer_low_score(self):
        """Off-topic but confident-sounding answer must score low."""
        self.env.reset("medium_1")
        action = AnswerInput(
            question_id="medium_1",
            student_answer=(
                "Binary search trees are used in databases and they are very fast "
                "and efficient for searching large datasets."
            )
        )
        _, reward, _, _ = self.env.step(action)
        assert reward < 0.6, f"Expected < 0.6 but got {reward}"

    def test_scores_are_not_all_equal(self):
        """If all scores are nearly identical, grader is broken."""
        answers = [
            ("easy_1", "Photosynthesis uses sunlight, water, carbon dioxide, chlorophyll to produce glucose and oxygen."),
            ("easy_1", "Plants do something with light."),
            ("easy_1", "I have no idea what photosynthesis is at all."),
        ]
        scores = []
        for task_id, ans in answers:
            self.env.reset(task_id)
            action = AnswerInput(question_id=task_id, student_answer=ans)
            _, reward, _, _ = self.env.step(action)
            scores.append(reward)

        # Spread between highest and lowest must be meaningful (> 0.3)
        assert max(scores) - min(scores) > 0.3, (
            f"Scores too similar — grader may be broken: {scores}"
        )

from models import EvaluationResult, EvaluationFeedback
from utils.helpers import match_concepts


class EvaluatorEngine:
    def __init__(self):
        pass

    def evaluate(self, answer_text: str, key_concepts: list[str]) -> EvaluationResult:
        """
        Evaluate a student answer against key concepts.
        Returns a score in the range [0.0, 1.0] with structured feedback.
        """
        if not key_concepts:
            return EvaluationResult(
                score=1.0,
                feedback=EvaluationFeedback(
                    covered_concepts=[],
                    missing_concepts=[],
                    weak_areas="No key concepts defined for this task.",
                    suggestions="N/A"
                )
            )

        if not answer_text or len(answer_text.strip()) < 5:
            return EvaluationResult(
                score=0.0,
                feedback=EvaluationFeedback(
                    covered_concepts=[],
                    missing_concepts=key_concepts,
                    weak_areas="Answer is too short or empty to evaluate.",
                    suggestions="Provide a detailed answer covering all required concepts."
                )
            )

        covered, missing = match_concepts(answer_text, key_concepts)

        total = len(key_concepts)
        coverage_score = len(covered) / total if total > 0 else 0.0

        # Apply a length-relevance penalty: very short but technically matching answers
        # get a mild penalty to reward completeness.
        word_count = len(answer_text.strip().split())
        length_bonus = min(1.0, word_count / 30)  # saturates at 30 words
        
        # Weighted: 85% concept coverage + 15% length/completeness signal
        raw_score = (coverage_score * 0.85) + (length_bonus * 0.15)
        
        # Clip to [0.0, 1.0]
        final_score = round(min(1.0, max(0.0, raw_score)), 4)

        # --- Weak areas feedback ---
        covered_ratio = len(covered) / total
        if covered_ratio == 0.0:
            weak_areas = "The answer fails to address any of the fundamental concepts expected."
        elif covered_ratio < 0.5:
            weak_areas = (
                f"The answer touches on the topic but misses major core ideas such as: "
                f"{', '.join(missing[:2])}."
            )
        elif covered_ratio < 1.0:
            weak_areas = "The answer is generally good but lacks completeness in specific areas."
        else:
            weak_areas = "All key concepts are covered. Well done!"

        # --- Suggestions ---
        if missing:
            suggestions = (
                f"Consider expanding your answer to include: {', '.join(missing)}. "
                "These are central to a complete response."
            )
        else:
            suggestions = "Great coverage! Review your answer for clarity and depth."

        return EvaluationResult(
            score=final_score,
            feedback=EvaluationFeedback(
                covered_concepts=covered,
                missing_concepts=missing,
                weak_areas=weak_areas,
                suggestions=suggestions
            )
        )

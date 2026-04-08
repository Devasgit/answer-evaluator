from pydantic import BaseModel, Field
from typing import List, Optional


class QuestionModel(BaseModel):
    id: str
    difficulty: str
    text: str
    key_concepts: List[str]


class AnswerInput(BaseModel):
    question_id: str
    student_answer: str


class EvaluationFeedback(BaseModel):
    missing_concepts: List[str]
    covered_concepts: List[str]
    weak_areas: str
    suggestions: str = ""


class EvaluationResult(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0.0 and 1.0")
    max_score: float = 1.0
    feedback: EvaluationFeedback

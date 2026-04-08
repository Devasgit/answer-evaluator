from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from models import AnswerInput, EvaluationResult
from tasks import get_tasks, get_task
from env import AnswerEvalEnv

app = FastAPI(
    title="Answer-Eval-Env API",
    version="1.0.0",
    description="AI-powered environment for grading descriptive student answers."
)

environment = AnswerEvalEnv()


class EvaluateRequest(BaseModel):
    taskId: str
    answer: str


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "system": "Answer-Eval-Env", "version": "1.0.0"}


# ── Task registry ─────────────────────────────────────────────────────────────

@app.get("/tasks", tags=["Tasks"])
def list_tasks():
    """Return the full list of available evaluation tasks."""
    return [task.model_dump() for task in get_tasks()]


@app.get("/tasks/{task_id}", tags=["Tasks"])
def get_task_by_id(task_id: str):
    """Return a single task by its ID."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return task.model_dump()


# ── Environment endpoints ─────────────────────────────────────────────────────

@app.post("/reset", tags=["Environment"])
def reset_environment(task_id: str):
    """
    Reset the environment for a given task_id.
    Returns the initial state.
    """
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    state, _ = environment.reset(task_id)
    return {"status": "reset", "state": state}


@app.get("/state", tags=["Environment"])
def get_state():
    """Return the current environment state."""
    try:
        return environment.state()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Evaluation endpoint ───────────────────────────────────────────────────────

@app.post("/evaluate", response_model=EvaluationResult, tags=["Evaluate"])
def evaluate_answer(request: EvaluateRequest):
    """
    Evaluate a student answer for the given task.
    Returns a score in [0.0, 1.0] and structured feedback.
    """
    task = get_task(request.taskId)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{request.taskId}' not found.")

    environment.reset(request.taskId)

    action = AnswerInput(question_id=request.taskId, student_answer=request.answer)
    _, _, _, info = environment.step(action)

    return info["evaluation"]


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=False)

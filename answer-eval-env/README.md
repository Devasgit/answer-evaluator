# Answer Eval Env — README

# answer-eval-env

A production-ready, **OpenEnv-compliant** AI evaluation environment for grading student descriptive answers. Built with FastAPI, Pydantic v2, and a deterministic grading engine based on key-concept coverage and fuzzy semantic matching.

---

## 📁 Project Structure

```
answer-eval-env/
├── api.py              # FastAPI application (REST interface)
├── env.py              # OpenEnv-style environment (reset / step)
├── grader.py           # Deterministic evaluation engine
├── inference.py        # Standalone validation script
├── models.py           # Pydantic v2 data models
├── tasks.py            # Predefined task registry (9 tasks)
├── test_eval.py        # Full unit + integration test suite
├── openenv.yaml        # OpenEnv spec manifest
├── requirements.txt    # Python dependencies
└── utils/
    └── helpers.py      # Text cleaning, fuzzy matching utilities
```

---

## ⚡ Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the validation inference
```bash
python inference.py
```

### 3. Start the API server
```bash
python api.py
```
The API will be available at `http://localhost:8080`.

---

## 🌐 API Endpoints

### `GET /`
Health check.
```json
{"status": "ok", "system": "Answer-Eval-Env"}
```

### `GET /tasks`
Returns all available tasks.
```json
[
  {
    "id": "easy_1",
    "difficulty": "easy",
    "text": "What is photosynthesis?",
    "key_concepts": ["sunlight", "water", "carbon dioxide", "oxygen", "glucose", "chlorophyll"]
  },
  ...
]
```

### `POST /evaluate`
Submit a student answer for evaluation.

**Request body:**
```json
{
  "taskId": "easy_1",
  "answer": "Plants use sunlight, water, and carbon dioxide to produce oxygen and glucose."
}
```

**Response:**
```json
{
  "score": 83.33,
  "max_score": 100.0,
  "feedback": {
    "covered_concepts": ["sunlight", "water", "carbon dioxide", "oxygen", "glucose"],
    "missing_concepts": ["chlorophyll"],
    "weak_areas": "The answer is generally good but lacks completeness in specific areas."
  }
}
```

---

## 📋 Available Tasks

| ID         | Difficulty | Topic                             |
|------------|------------|-----------------------------------|
| `easy_1`   | Easy       | What is photosynthesis?           |
| `easy_2`   | Easy       | Define kinetic energy.            |
| `easy_3`   | Easy       | What is a network protocol?       |
| `medium_1` | Medium     | How does a binary search tree work? |
| `medium_2` | Medium     | Describe the water cycle.         |
| `medium_3` | Medium     | Differences between RAM and ROM?  |
| `hard_1`   | Hard       | Explain quantum entanglement.     |
| `hard_2`   | Hard       | Impact of the Industrial Revolution. |
| `hard_3`   | Hard       | How does Transformer architecture work? |

---

## 🧠 How Grading Works

1. **Key Concept Matching** — The answer is checked for each expected concept using exact substring match first.
2. **Fuzzy Sliding Window** — If exact match fails, a sliding window of n-grams is compared using `SequenceMatcher` with a configurable threshold (default: `0.75`).
3. **Score Calculation** — `score = (covered / total_concepts) * 100`
4. **Feedback Generation** — Covered/missing concepts and a weak-area diagnosis are returned.

### Robustness
- Short/empty answers score `0` regardless of content.
- Off-topic confident-sounding answers score low (concept-grounded, not fluency-grounded).
- Minor typos are tolerated via fuzzy matching.

---

## 🧪 Running Tests

```bash
pip install pytest
python -m pytest test_eval.py -v
```

Expected: **all 25 tests pass**.

---

## 📄 OpenEnv Spec

See [`openenv.yaml`](./openenv.yaml) for the full environment specification.

- **State**: `question`, `concepts`, `difficulty`, `student_answer`
- **Action**: `{ question_id, student_answer }`
- **Reward**: `float` in `[0.0, 100.0]`

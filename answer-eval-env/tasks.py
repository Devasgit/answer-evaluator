from models import QuestionModel

TASKS = {
    "easy_1": QuestionModel(
        id="easy_1",
        difficulty="easy",
        text="What is photosynthesis?",
        key_concepts=["sunlight", "water", "carbon dioxide", "oxygen", "glucose", "chlorophyll"]
    ),
    "easy_2": QuestionModel(
        id="easy_2",
        difficulty="easy",
        text="Define kinetic energy.",
        key_concepts=["energy", "motion", "mass", "velocity"]
    ),
    "easy_3": QuestionModel(
        id="easy_3",
        difficulty="easy",
        text="What is a network protocol?",
        key_concepts=["rules", "communication", "data transfer", "network"]
    ),
    "medium_1": QuestionModel(
        id="medium_1",
        difficulty="medium",
        text="Explain how a binary search tree works.",
        key_concepts=["nodes", "left child", "right child", "greater than", "less than", "log n"]
    ),
    "medium_2": QuestionModel(
        id="medium_2",
        difficulty="medium",
        text="Describe the water cycle.",
        key_concepts=["evaporation", "condensation", "precipitation", "collection", "vapor"]
    ),
    "medium_3": QuestionModel(
        id="medium_3",
        difficulty="medium",
        text="What are the differences between RAM and ROM?",
        key_concepts=["volatile", "non-volatile", "read", "write", "temporary", "permanent"]
    ),
    "hard_1": QuestionModel(
        id="hard_1",
        difficulty="hard",
        text="Explain the concept of quantum entanglement.",
        key_concepts=["particles", "interconnected", "state", "distance", "superposition", "instantaneous"]
    ),
    "hard_2": QuestionModel(
        id="hard_2",
        difficulty="hard",
        text="Discuss the impact of the Industrial Revolution on modern society.",
        key_concepts=["urbanization", "mass production", "factories", "steam engine", "labor laws", "economic shift"]
    ),
    "hard_3": QuestionModel(
        id="hard_3",
        difficulty="hard",
        text="How does the Transformer architecture work in deep learning?",
        key_concepts=["self-attention", "parallelization", "encoder", "decoder", "positional encoding", "context"]
    )
}

def get_tasks():
    return list(TASKS.values())

def get_task(task_id: str):
    return TASKS.get(task_id)

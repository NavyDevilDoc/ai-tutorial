"""Display strings and configuration constants for the AI Literacy Tutor."""

APP_TITLE: str = "AI Literacy Tutor"
APP_SUBTITLE: str = "Plain-language AI/ML definitions for business professionals"
SEARCH_PLACEHOLDER: str = "Search for a term\u2026"
ALL_CATEGORIES_LABEL: str = "All Categories"
TERM_NOT_FOUND_MSG: str = "Term not found. Try a different search."
ALL_DIFFICULTIES_LABEL: str = "All Levels"
DIFFICULTY_LABELS: list[str] = ["All Levels", "Beginner", "Intermediate", "Advanced"]

MAX_HISTORY_DEPTH: int = 10

WELCOME_HEADING: str = "What do you want to learn about?"
WELCOME_SUBTEXT: str = (
    "Type an AI or ML term you've heard in a meeting, read in a report,"
    " or just want to understand better."
)
QUICK_START_SLUGS: list[str] = [
    "large-language-model",
    "hallucination",
    "supervised-learning",
    "overfitting",
    "retrieval-augmented-generation",
    "a-b-testing",
]

ANALOGY_PREFIX: str = "\U0001f4a1 Analogy"
SENTENCE_PREFIX: str = "\U0001f4bc Use in a Sentence"

DIFFICULTY_COLORS: dict[str, str] = {
    "beginner": "green",
    "intermediate": "orange",
    "advanced": "red",
}

CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    "ml_fundamentals": "ML Fundamentals",
    "neural_networks": "Neural Networks",
    "nlp": "Natural Language Processing",
    "computer_vision": "Computer Vision",
    "mlops": "MLOps & Deployment",
    "statistics": "Statistics & Math",
    "generative_ai": "Generative AI",
    "ai_ethics": "AI Ethics & Governance",
    "business_strategy": "Business & Strategy",
}

import type { Difficulty } from "./models";

export const APP_TITLE = "AI Literacy Tutor";
export const APP_SUBTITLE =
  "Plain-language AI/ML definitions for business professionals";
export const SEARCH_PLACEHOLDER = "Search for a term…";
export const ALL_CATEGORIES_LABEL = "All Categories";
export const TERM_NOT_FOUND_MSG = "Term not found. Try a different search.";
export const ALL_DIFFICULTIES_LABEL = "All Levels";

export const MAX_HISTORY_DEPTH = 10;

export const WELCOME_HEADING = "What do you want to learn about?";
export const WELCOME_SUBTEXT =
  "Type an AI or ML term you've heard in a meeting, read in a report, or just want to understand better.";

export const QUICK_START_SLUGS: readonly string[] = [
  "large-language-model",
  "hallucination",
  "supervised-learning",
  "overfitting",
  "retrieval-augmented-generation",
  "a-b-testing",
];

export const ANALOGY_PREFIX = "\u{1f4a1} Analogy";
export const SENTENCE_PREFIX = "\u{1f4bc} Use in a Sentence";

export const SUGGEST_TERM_HEADING = "Suggest a New Term";
export const SUGGEST_TERM_SUBTEXT =
  "Know an AI/ML term that should be in our glossary? Submit a suggestion and we'll review it.";
export const SUGGEST_SUCCESS_MSG =
  "Thanks! Your suggestion has been submitted for review.";
export const SUGGEST_RATE_LIMIT_MSG =
  "You've already submitted a suggestion this session. Please try again later.";
export const SUGGEST_ERROR_MSG =
  "Something went wrong submitting your suggestion. Please try again.";

export const DIFFICULTY_COLORS: Record<Difficulty, string> = {
  beginner: "#2ca02c",
  intermediate: "#ff7f0e",
  advanced: "#d62728",
};

export const CATEGORY_DISPLAY_NAMES: Record<string, string> = {
  ml_fundamentals: "ML Fundamentals",
  neural_networks: "Neural Networks",
  nlp: "Natural Language Processing",
  computer_vision: "Computer Vision",
  mlops: "MLOps & Deployment",
  statistics: "Statistics & Math",
  generative_ai: "Generative AI",
  ai_ethics: "AI Ethics & Governance",
  business_strategy: "Business & Strategy",
};

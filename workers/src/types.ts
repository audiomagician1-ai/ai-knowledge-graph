export interface Env {
  DB: D1Database;
  OPENROUTER_API_KEY?: string;
  OPENAI_API_KEY?: string;
  DEEPSEEK_API_KEY?: string;
  CORS_ORIGINS?: string;
  /** Default LLM model for dialogue (default: google/gemma-4-31b-it:free) */
  LLM_MODEL_DIALOGUE?: string;
  /** Default LLM model for assessment (default: google/gemma-4-31b-it:free) */
  LLM_MODEL_ASSESSMENT?: string;
  /** Default LLM model for simple tasks (default: google/gemma-4-31b-it:free) */
  LLM_MODEL_SIMPLE?: string;
}

export interface UserLLMConfig {
  provider: string;
  api_key: string;
  model?: string;
  base_url?: string;
}

export interface AssessmentResult {
  completeness: number;
  accuracy: number;
  depth: number;
  examples: number;
  overall_score: number;
  gaps: string[];
  feedback: string;
  mastered: boolean;
}

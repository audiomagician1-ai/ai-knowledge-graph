export interface Env {
  DB: D1Database;
  OPENROUTER_API_KEY?: string;
  OPENAI_API_KEY?: string;
  DEEPSEEK_API_KEY?: string;
  CORS_ORIGINS?: string;
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

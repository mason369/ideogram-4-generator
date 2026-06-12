export type ExecutionMode = "local_plain" | "local_json" | "official_magic";
export type SamplerPreset = "V4_QUALITY_48" | "V4_DEFAULT_20" | "V4_TURBO_12";

export interface FormState {
  prompt: string;
  width: number;
  height: number;
  sampler_preset: SamplerPreset;
  seed: number;
  candidate_count: number;
  execution_mode: ExecutionMode;
  api_key: string;
}

export interface AppConfig {
  defaults: Omit<FormState, "api_key">;
  canvas_presets: Array<{ key: string; width: number; height: number }>;
  sampler_presets: SamplerPreset[];
  candidate_counts: number[];
}

export interface GeneratedImage {
  url: string;
  filename: string;
  seed?: number | null;
  prompt?: string | null;
  resolution?: string | null;
}

export interface IdeogramResult {
  mode: ExecutionMode;
  images: GeneratedImage[];
  request: Record<string, unknown>;
  optimized_prompt?: unknown;
  message: string;
}

export interface MagicPromptResult {
  aspect_ratio: string;
  optimized_prompt: unknown;
  request: Record<string, unknown>;
  message: string;
}

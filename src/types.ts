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
  enable_copyright_detection: boolean;
}

export interface AppConfig {
  defaults: Omit<FormState, "api_key" | "enable_copyright_detection">;
  canvas_presets: Array<{ key: string; width: number; height: number }>;
  sampler_presets: SamplerPreset[];
  candidate_counts: number[];
  official_resolutions: string[];
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

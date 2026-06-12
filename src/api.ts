import type { AppConfig, FormState, IdeogramResult } from "./types";

export async function loadConfig(): Promise<AppConfig> {
  const response = await fetch("/api/config");
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function generateImage(form: FormState): Promise<IdeogramResult> {
  const response = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt: form.prompt.trim(),
      width: form.width,
      height: form.height,
      sampler_preset: form.sampler_preset,
      seed: form.seed,
      candidate_count: form.candidate_count,
      execution_mode: form.execution_mode,
      api_key: form.api_key.trim() || null,
      enable_copyright_detection:
        form.execution_mode === "official_magic" ? form.enable_copyright_detection : null
    })
  });
  if (!response.ok) {
    let message = await response.text();
    try {
      const parsed = JSON.parse(message);
      message = parsed.detail || message;
    } catch {
      // Preserve the raw response text.
    }
    throw new Error(message);
  }
  return response.json();
}

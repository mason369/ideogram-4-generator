import {
  BadgeCheck,
  Cpu,
  Dices,
  ExternalLink,
  ImageIcon,
  KeyRound,
  Languages,
  Loader2,
  Send,
  Server,
  WandSparkles
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { generateImage, loadConfig } from "./api";
import { messages, translate, type Locale } from "./i18n";
import type { AppConfig, ExecutionMode, FormState, IdeogramResult, SamplerPreset } from "./types";

const SAMPLE_IMAGES = [
  "/tool-assets/ideogram/ideogram-sample-poster.jpg",
  "/tool-assets/ideogram/ideogram-sample-product.jpg",
  "/tool-assets/ideogram/ideogram-sample-photo.jpg",
  "/tool-assets/ideogram/ideogram-sample-illustration.jpg"
];

const DEFAULT_FORM: FormState = {
  prompt: "",
  width: 2048,
  height: 2048,
  sampler_preset: "V4_QUALITY_48",
  seed: 0,
  candidate_count: 1,
  execution_mode: "local_plain",
  api_key: "",
  enable_copyright_detection: false
};

function randomSeed() {
  return Math.floor(Math.random() * 2147483647) + 1;
}

function FieldLabel({
  label,
  description
}: {
  label: string;
  description?: string;
}) {
  return (
    <span className="field-label">
      <span>{label}</span>
      {description ? <small>{description}</small> : null}
    </span>
  );
}

function Badge({ children, variant = "neutral" }: { children: string; variant?: "accent" | "neutral" }) {
  return <span className={`badge badge-${variant}`}>{children}</span>;
}

function Segment({
  selected,
  label,
  icon,
  onClick
}: {
  selected: boolean;
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button type="button" className={`segment ${selected ? "segment-selected" : ""}`} onClick={onClick}>
      {icon}
      <span>{label}</span>
    </button>
  );
}

function ModelSpotlight({ locale, t }: { locale: Locale; t: (key: string) => string }) {
  const sampleLabels = messages[locale].spotlight.sampleTiles;
  return (
    <section className="spotlight">
      <div className="sample-mosaic" role="img" aria-label={t("spotlight.sampleCaption")}>
        {SAMPLE_IMAGES.map((image, index) => (
          <div className="sample-tile" key={image} style={{ backgroundImage: `url(${image})` }}>
            <span>{sampleLabels[index]}</span>
          </div>
        ))}
        <div className="sample-caption">
          <p>{t("spotlight.sampleEyebrow")}</p>
          <span>{t("spotlight.sampleCaption")}</span>
        </div>
      </div>
      <div className="spotlight-body">
        <div className="spotlight-heading">
          <div>
            <p className="eyebrow">{t("spotlight.eyebrow")}</p>
            <h2>{t("spotlight.title")}</h2>
            <p>{t("spotlight.body")}</p>
          </div>
          <a href="https://huggingface.co/ideogram-ai/ideogram-4-nf4" target="_blank" rel="noreferrer">
            {t("source")}
            <ExternalLink size={14} />
          </a>
        </div>
        <div className="highlight-grid">
          {messages[locale].spotlight.highlights.map((item) => (
            <div className="highlight" key={item}>
              <BadgeCheck size={16} />
              <p>{item}</p>
            </div>
          ))}
        </div>
        <div className="recommendations">
          <p>{t("spotlight.recommendedTitle")}</p>
          <div>
            {messages[locale].spotlight.recommendations.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function creditCost(form: FormState) {
  const pixels = Math.max(1, form.width * form.height);
  const anchors = {
    V4_QUALITY_48: { one: 5, four: 12 },
    V4_DEFAULT_20: { one: 3, four: 7 },
    V4_TURBO_12: { one: 2, four: 4 }
  }[form.sampler_preset];
  const oneMp = 1024 * 1024;
  const fourMp = 2048 * 2048;
  const single =
    pixels <= oneMp
      ? Math.max(1, Math.ceil((anchors.one * pixels) / oneMp))
      : Math.ceil(anchors.one + (anchors.four - anchors.one) * ((Math.min(pixels, fourMp) - oneMp) / (fourMp - oneMp)));
  return single * form.candidate_count;
}

export default function App() {
  const [locale, setLocale] = useState<Locale>(() => (localStorage.getItem("locale") as Locale) || "zh_CN");
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [result, setResult] = useState<IdeogramResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const t = (key: string, values?: Record<string, string | number>) => translate(locale, key, values);

  useEffect(() => {
    localStorage.setItem("locale", locale);
  }, [locale]);

  useEffect(() => {
    loadConfig()
      .then((data) => {
        setConfig(data);
        setForm((prev) => ({ ...prev, ...data.defaults }));
      })
      .catch((exc) => setError(String(exc)));
  }, []);

  const officialResolutionSupported = config?.official_resolutions.includes(`${form.width}x${form.height}`) ?? false;
  const canSubmit = form.prompt.trim().length > 0 && !loading;

  const preview = useMemo(() => {
    return {
      prompt: form.prompt.trim(),
      width: form.width,
      height: form.height,
      sampler_preset: form.sampler_preset,
      seed: form.seed,
      candidate_count: form.candidate_count,
      execution_mode: form.execution_mode,
      api_key: form.api_key ? "[hidden]" : null,
      enable_copyright_detection:
        form.execution_mode === "official_magic" ? form.enable_copyright_detection : null
    };
  }, [form]);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function submit() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await generateImage(form);
      setResult(data);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  }

  const samplerName = t(`samplerPresets.${form.sampler_preset}`);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span>
            <ImageIcon size={22} />
          </span>
          <div>
            <h1>{t("appTitle")}</h1>
            <p>{t("appSubtitle")}</p>
          </div>
        </div>
        <div className="top-actions">
          <a href="https://github.com/mason369/ideogram-4-generator#readme" target="_blank" rel="noreferrer">
            {t("navDocs")}
            <ExternalLink size={14} />
          </a>
          <button
            type="button"
            className="language-button"
            onClick={() => setLocale(locale === "zh_CN" ? "en_US" : "zh_CN")}
          >
            <Languages size={16} />
            {messages[locale === "zh_CN" ? "en_US" : "zh_CN"].languageName}
          </button>
        </div>
      </header>

      <main>
        <section className="intro-card">
          <div className="intro-heading">
            <span className="tool-icon">
              <ImageIcon size={22} />
            </span>
            <div>
              <h2>{t("title")}</h2>
              <p>{t("subtitle")}</p>
            </div>
          </div>
          <div className="badges">
            <Badge variant="accent">{`${form.width}x${form.height} · ${samplerName}`}</Badge>
            <Badge>{t("creditsBadge", { cost: creditCost(form) })}</Badge>
          </div>

          <div className="mode-box">
            <FieldLabel label={t("modeLabel")} description={t(`modeDescriptions.${form.execution_mode}`)} />
            <div className="segments">
              <Segment
                selected={form.execution_mode === "local_plain"}
                label={t("modes.local_plain")}
                icon={<Cpu size={16} />}
                onClick={() => update("execution_mode", "local_plain")}
              />
              <Segment
                selected={form.execution_mode === "local_json"}
                label={t("modes.local_json")}
                icon={<Server size={16} />}
                onClick={() => update("execution_mode", "local_json")}
              />
              <Segment
                selected={form.execution_mode === "official_magic"}
                label={t("modes.official_magic")}
                icon={<WandSparkles size={16} />}
                onClick={() => update("execution_mode", "official_magic")}
              />
            </div>
          </div>

          {form.execution_mode === "official_magic" ? (
            <div className="api-row">
              <label className="api-key-field">
                <FieldLabel label={t("apiKey")} />
                <span>
                  <KeyRound size={16} />
                  <input
                    type="password"
                    value={form.api_key}
                    placeholder={t("apiKeyPlaceholder")}
                    onChange={(event) => update("api_key", event.target.value)}
                  />
                </span>
              </label>
              <label className="check-field">
                <input
                  type="checkbox"
                  checked={form.enable_copyright_detection}
                  onChange={(event) => update("enable_copyright_detection", event.target.checked)}
                />
                {t("copyrightDetection")}
              </label>
            </div>
          ) : null}

          <label className="prompt-field">
            <FieldLabel label={t("promptLabel")} description={t("promptDescription")} />
            <textarea
              value={form.prompt}
              maxLength={4000}
              rows={7}
              placeholder={t("promptPlaceholder")}
              onChange={(event) => update("prompt", event.target.value)}
            />
            <span>{form.prompt.length}/4000</span>
          </label>
        </section>

        <ModelSpotlight locale={locale} t={t} />

        <section className="workspace-grid">
          <div className="panel">
            <div className="dimension-grid">
              <label>
                <FieldLabel label={t("width")} description={t("dimensionsDescription")} />
                <input
                  type="number"
                  min={256}
                  max={2048}
                  step={16}
                  value={form.width}
                  onChange={(event) => update("width", Number.parseInt(event.target.value || "0", 10))}
                />
              </label>
              <label>
                <FieldLabel label={t("height")} description={t("aspectDescription")} />
                <input
                  type="number"
                  min={256}
                  max={2048}
                  step={16}
                  value={form.height}
                  onChange={(event) => update("height", Number.parseInt(event.target.value || "0", 10))}
                />
              </label>
            </div>
            {form.execution_mode === "official_magic" && !officialResolutionSupported ? (
              <p className="warning-text">{t("officialResolutionWarning")}</p>
            ) : null}
            <div className="preset-row">
              <FieldLabel label={t("presetsLabel")} />
              <div>
                {(config?.canvas_presets || []).map((preset) => (
                  <button
                    type="button"
                    key={preset.key}
                    className={form.width === preset.width && form.height === preset.height ? "preset selected" : "preset"}
                    onClick={() => {
                      update("width", preset.width);
                      update("height", preset.height);
                    }}
                  >
                    {t(`quickSizes.${preset.key}`)}
                  </button>
                ))}
              </div>
            </div>
            <div className="seed-field">
              <FieldLabel label={t("seed")} description={t("seedDescription")} />
              <div className="seed-control">
                <input
                  type="number"
                  min={0}
                  max={2147483647}
                  placeholder="123456789"
                  value={form.seed}
                  aria-label={t("seed")}
                  onChange={(event) => update("seed", Number.parseInt(event.target.value || "0", 10))}
                />
                <button
                  type="button"
                  aria-label={t("randomSeed")}
                  title={t("randomSeed")}
                  onClick={() => update("seed", randomSeed())}
                >
                  <Dices size={20} />
                </button>
              </div>
            </div>
          </div>

          <div className="panel">
            <label>
              <FieldLabel label={t("samplerPreset")} description={t("samplerDescription")} />
              <select
                value={form.sampler_preset}
                onChange={(event) => update("sampler_preset", event.target.value as SamplerPreset)}
              >
                {(config?.sampler_presets || ["V4_QUALITY_48", "V4_DEFAULT_20", "V4_TURBO_12"]).map((value) => (
                  <option key={value} value={value}>
                    {t(`samplerPresets.${value}`)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <FieldLabel label={t("candidateCount")} description={t("candidateDescription")} />
              <select
                value={form.candidate_count}
                onChange={(event) => update("candidate_count", Number.parseInt(event.target.value, 10))}
              >
                {(config?.candidate_counts || [1, 2, 3, 4]).map((value) => (
                  <option key={value} value={value}>
                    {messages[locale].candidateCounts[value as 1 | 2 | 3 | 4]}
                  </option>
                ))}
              </select>
            </label>
            <div className="run-summary">
              <WandSparkles size={18} />
              <p>{t("runSummary", { width: form.width, height: form.height, preset: form.sampler_preset, count: form.candidate_count })}</p>
            </div>
          </div>
        </section>

        <button className="submit-button" type="button" disabled={!canSubmit} onClick={submit}>
          {loading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
          {loading ? t("processing") : t("submit")}
        </button>

        {error ? (
          <section className="error-panel">
            <strong>{t("errorTitle")}</strong>
            <pre>{error}</pre>
          </section>
        ) : null}

        <section className="result-grid">
          <div className="panel preview-panel">
            <h3>{t("requestPreview")}</h3>
            <pre>{JSON.stringify(preview, null, 2)}</pre>
          </div>
          <div className="panel output-panel">
            <h3>{t("resultPreview")}</h3>
            {result ? (
              <>
                <div className="image-grid">
                  {result.images.map((image) => (
                    <a href={image.url} target="_blank" rel="noreferrer" key={image.filename} className="result-image">
                      <img src={image.url} alt={image.filename} />
                      <span>
                        {image.filename}
                        {image.seed ? ` · seed ${image.seed}` : ""}
                      </span>
                    </a>
                  ))}
                </div>
                {result.optimized_prompt ? (
                  <>
                    <h4>{t("optimizedPrompt")}</h4>
                    <pre>{JSON.stringify(result.optimized_prompt, null, 2)}</pre>
                  </>
                ) : null}
              </>
            ) : (
              <p className="empty-state">{t("noResult")}</p>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

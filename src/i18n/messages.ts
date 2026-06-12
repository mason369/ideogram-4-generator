export const messages = {
  zh_CN: {
    languageName: "中文",
    appTitle: "Ideogram 4 图像生成器",
    appSubtitle: "复刻 TelkNet Ideogram 4 工具的本地 CUDA 与官方 Magic Prompt 界面",
    navDocs: "README",
    title: "提示词生成图像",
    subtitle: "使用 Ideogram 4 开放权重本地运行，或输入 API Key 走官方 Magic Prompt 优化链路。",
    qualityBadge: "最高 2048x2048",
    creditsBadge: "{cost} 积分估算",
    promptLabel: "提示词",
    promptDescription: "描述主体、可见文字、构图、风格和输出用途。",
    promptPlaceholder: "一张 TelkNet Studio 精致海报，清晰编辑排版，可读标题文字，高对比产品设计...",
    modeLabel: "调用链路",
    modes: {
      local_plain: "本地原文提示词",
      local_json: "本地结构化 JSON",
      official_magic: "官方提示词优化"
    },
    modeDescriptions: {
      local_plain: "不接入官方提示词优化；自然语言按原文送入本地 Ideogram 4 运行时。",
      local_json: "手写 Ideogram 4 JSON caption，直接送入本地模型。",
      official_magic: "输入 API Key，仅调用官方 Magic Prompt；返回的 JSON prompt 继续交给本地 CUDA 出图。"
    },
    apiKey: "Ideogram API Key",
    apiKeyPlaceholder: "仅本次浏览器会话使用，不写入仓库",
    width: "宽度",
    height: "高度",
    dimensionsDescription: "所有生成模式都使用本地 256-2048 px 画布。",
    aspectDescription: "本地比例保持 1:6 到 6:1；官方 Magic Prompt 只接收支持的比例桶。",
    presetsLabel: "画布预设",
    quickSizes: {
      square2k: "方图 2K",
      portrait9x16: "竖版 9:16",
      landscape16x9: "横版 16:9",
      poster2x3: "海报 2:3",
      wide4x1: "宽幅 4:1",
      tall1x4: "长图 1:4"
    },
    seed: "SEED（可选）",
    seedDescription: "0 表示运行时随机；点击骰子会生成固定 seed。",
    randomSeed: "随机 SEED",
    samplerPreset: "采样预设",
    samplerDescription: "V4_QUALITY_48 是本地开放权重质量预设。",
    samplerPresets: {
      V4_QUALITY_48: "V4 Quality 48",
      V4_DEFAULT_20: "V4 Default 20",
      V4_TURBO_12: "V4 Turbo 12"
    },
    candidateCount: "候选图数量",
    candidateDescription: "一次生成 1 到 4 张；官方模式也只优化提示词，出图仍走本地。",
    candidateCounts: {
      1: "1 张",
      2: "2 张",
      3: "3 张",
      4: "4 张"
    },
    runSummary: "{width}x{height}，{preset}，{count} 张",
    submit: "生成图像",
    processing: "处理中",
    optimizeOnly: "仅优化提示词",
    optimizing: "优化中",
    requestPreview: "请求预览",
    resultPreview: "结果",
    optimizedPrompt: "优化后的 JSON Prompt",
    noResult: "生成后会在这里显示本地 PNG；仅优化提示词时会显示官方 JSON Prompt。",
    errorTitle: "生成失败",
    source: "模型卡",
    spotlight: {
      sampleEyebrow: "官方样例裁剪",
      sampleCaption: "样例图来自 TelkNet 原工具资源，标签由当前语言实时切换。",
      sampleTiles: ["海报氛围", "产品视觉", "品牌摄影", "插画场景"],
      eyebrow: "模型亮点",
      title: "开放权重图像模型中的顶尖设计选择",
      body: "Ideogram 4 是官方公开的 9.3B 开放权重文生图基础模型，重点面向设计、文字排版、结构化布局和原生 2K 生成。",
      highlights: [
        "官方定位：设计前沿的开放权重图像模型。",
        "擅长可读文字、Logo、标题、海报布局和品牌设计场景。",
        "支持原生 2048x2048 级画布生成，适合需要细节的 PNG 输出。"
      ],
      recommendedTitle: "推荐配置",
      recommendations: ["画布：最高 2048x2048 px", "采样：V4_QUALITY_48", "提示词：按所选链路显式处理"]
    }
  },
  en_US: {
    languageName: "English",
    appTitle: "Ideogram 4 Generator",
    appSubtitle: "A TelkNet-style Ideogram 4 tool with local CUDA and official Magic Prompt",
    navDocs: "README",
    title: "Prompt to Image",
    subtitle: "Run Ideogram 4 open weights locally, or enter an API key to use the official Magic Prompt flow.",
    qualityBadge: "Up to 2048x2048",
    creditsBadge: "{cost} credit estimate",
    promptLabel: "Prompt",
    promptDescription: "Describe the subject, visible text, composition, style, and intended output.",
    promptPlaceholder: "A refined TelkNet Studio poster, editorial typography, readable title text, high-contrast product design...",
    modeLabel: "Execution Flow",
    modes: {
      local_plain: "Local plain prompt",
      local_json: "Local structured JSON",
      official_magic: "Official Magic Prompt"
    },
    modeDescriptions: {
      local_plain: "No official prompt optimization; the natural-language prompt is sent to the local Ideogram 4 runtime verbatim.",
      local_json: "Use a hand-written Ideogram 4 JSON caption directly with the local model.",
      official_magic: "Enter an API key to call official Magic Prompt only; the returned JSON prompt is generated locally with CUDA."
    },
    apiKey: "Ideogram API Key",
    apiKeyPlaceholder: "Used for this browser session only; never committed",
    width: "Width",
    height: "Height",
    dimensionsDescription: "All generation modes use the local 256-2048 px canvas.",
    aspectDescription: "Local aspect ratio stays between 1:6 and 6:1; official Magic Prompt accepts supported aspect buckets only.",
    presetsLabel: "Canvas Presets",
    quickSizes: {
      square2k: "Square 2K",
      portrait9x16: "Portrait 9:16",
      landscape16x9: "Landscape 16:9",
      poster2x3: "Poster 2:3",
      wide4x1: "Wide 4:1",
      tall1x4: "Tall 1:4"
    },
    seed: "SEED (Optional)",
    seedDescription: "0 lets the runtime randomize; click the dice to write a fixed seed.",
    randomSeed: "Random SEED",
    samplerPreset: "Sampler Preset",
    samplerDescription: "V4_QUALITY_48 is the local open-weight quality preset.",
    samplerPresets: {
      V4_QUALITY_48: "V4 Quality 48",
      V4_DEFAULT_20: "V4 Default 20",
      V4_TURBO_12: "V4 Turbo 12"
    },
    candidateCount: "Candidate Count",
    candidateDescription: "Generate 1 to 4 candidates; official mode only optimizes the prompt and still renders locally.",
    candidateCounts: {
      1: "1 image",
      2: "2 images",
      3: "3 images",
      4: "4 images"
    },
    runSummary: "{width}x{height}, {preset}, {count} image(s)",
    submit: "Generate Image",
    processing: "Processing",
    optimizeOnly: "Optimize Prompt Only",
    optimizing: "Optimizing",
    requestPreview: "Request Preview",
    resultPreview: "Result",
    optimizedPrompt: "Optimized JSON Prompt",
    noResult: "Local PNG files appear here after generation; prompt-only optimization shows the official JSON Prompt.",
    errorTitle: "Generation Failed",
    source: "Model card",
    spotlight: {
      sampleEyebrow: "Official sample crops",
      sampleCaption: "Sample images are reused from the original TelkNet tool assets; labels switch with the current language.",
      sampleTiles: ["Poster mood", "Product visual", "Brand photo", "Illustrated scene"],
      eyebrow: "Model Highlights",
      title: "A leading open-weight choice for design images",
      body: "Ideogram 4 is an official 9.3B open-weight text-to-image foundation model focused on design, typography, structured layout, and native 2K generation.",
      highlights: [
        "Official positioning: an open-weight image model at the forefront of design.",
        "Strong at readable text, logos, headlines, posters, and brand design scenes.",
        "Supports native 2048x2048-class canvases for detailed PNG output."
      ],
      recommendedTitle: "Recommended Setup",
      recommendations: ["Canvas: up to 2048x2048 px", "Sampler: V4_QUALITY_48", "Prompt: handled explicitly by the selected flow"]
    }
  }
} as const;

export type Locale = keyof typeof messages;
export type MessageTree = (typeof messages)["zh_CN"];

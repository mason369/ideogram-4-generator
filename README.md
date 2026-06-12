# Ideogram 4 图像生成器

<p align="center">
  中文 | <a href="./docs/README.en.md">English</a>
</p>

复刻 TelkNet 项目中 `Ideogram 4` 图像生成工具的开源独立版。它保留原工具的参数习惯：`prompt / width / height / sampler_preset / seed / candidate_count`，并提供两条明确链路：

- **本地 CUDA 开放权重链路**：默认模式，不接入官方 Magic Prompt；自然语言提示词按原文送入本地 Ideogram 4 运行时。
- **官方提示词优化链路**：输入 Ideogram API Key 后，先调用官方 `/v1/ideogram-v4/magic-prompt`，再将返回的 `json_prompt` 送入官方 `/v1/ideogram-v4/generate`。

> 在线体验入口可按需部署到你自己的服务器；本仓库默认启动本地 Web 界面 `http://127.0.0.1:7860`。

## 截图

| Windows | Linux |
|---------|-------|
| ![Windows 界面](docs/Windows界面.png) | ![Linux 界面](docs/Linux界面.png) |

## 当前能力

- **复刻 TelkNet Ideogram 工具界面**：顶部工具卡、提示词输入、模型亮点、画布预设、采样预设、候选图数量和生成按钮保持同类结构。
- **中文默认 + 英文切换**：界面默认中文，可在右上角切换 English；README 同步提供中英两版。
- **Seed 控件**：前端提供 `SEED（可选）` 输入框和骰子按钮；`0` 表示运行时随机，点击骰子生成固定 seed。
- **本地开放权重模式**：通过官方 `ideogram-oss/ideogram4` 推理包调用 `ideogram-ai/ideogram-4-nf4` 或 `fp8` 权重。
- **官方 API 模式**：封装 API Key、Magic Prompt、Generate v4 和图片下载，生成后的临时 URL 会被下载到本地 `runtime/outputs/`。
- **严格参数校验**：尺寸范围 `256-2048`，步进 `16`，最大宽高比 `6:1`；候选图 `1-4`；seed 范围 `0-2147483647`。
- **不做静默降级**：缺少 API Key、缺少 HF_TOKEN、尺寸不在官方 v4 固定 resolution 列表、CUDA 不可用或权重未授权时都会显式失败。
- **GitHub Actions 发布**：支持 Windows / Linux GPU 便携包，release workflow 会下载并打包 Ideogram 4 NF4 权重缓存。

## 调用链路说明

| 模式 | UI 名称 | 是否接入官方提示词优化 | 输入 | 输出 |
|------|---------|------------------------|------|------|
| `local_plain` | 本地原文提示词 | 否 | 自然语言 prompt | 本地 PNG |
| `local_json` | 本地结构化 JSON | 否 | Ideogram 4 JSON caption | 本地 PNG |
| `official_magic` | 官方提示词优化 | 是 | 自然语言 prompt + API Key | 官方 API PNG 下载副本 |

本地模式和 TelkNet 原工具一致保留任意 `256-2048`、16 步进画布；官方 v4 API 当前只接受固定 `resolution` 枚举，所以官方模式会严格检查尺寸，不会自动改成“最接近”的尺寸。

## 快速开始

### 方式 1：官方 API 模式（无需本地 GPU）

```bash
git clone https://github.com/mason369/ideogram-4-generator.git
cd ideogram-4-generator

python -m venv venv310
venv310\Scripts\python -m pip install -r requirements.txt  # Windows
# source venv310/bin/activate && pip install -r requirements.txt  # Linux

npm install
npm run build
venv310\Scripts\python run.py
```

打开 `http://127.0.0.1:7860`，选择 **官方提示词优化**，输入 Ideogram API Key 后生成。

### 方式 2：本地 CUDA 开放权重模式

先安装官方运行时并接受 Hugging Face 权重许可：

```bash
python install.py --no-run
python tools/download_ideogram_weights.py --repo-id ideogram-ai/ideogram-4-nf4 --cache-dir models/hf-cache
python run.py
```

必需条件：

- 已在 Hugging Face 接受 `ideogram-ai/ideogram-4-nf4` 权重许可。
- 环境变量 `HF_TOKEN` 已设置。
- NVIDIA CUDA GPU；`nf4` 是 CUDA 路径。
- 已安装 `git+https://github.com/ideogram-oss/ideogram4.git`。

### 常用环境变量

| 变量 | 说明 |
|------|------|
| `IDEOGRAM_API_KEY` | 官方 API Key；UI 输入为空时读取 |
| `HF_TOKEN` | 下载 gated 权重 |
| `IDEOGRAM_QUANTIZATION` | `nf4` 或 `fp8`，默认 `nf4` |
| `IDEOGRAM_DEVICE` | 默认 `cuda` |
| `IDEOGRAM_HF_CACHE` | 指向已下载的 Hugging Face cache |
| `IDEOGRAM_OUTPUT_DIR` | 输出目录，默认 `runtime/outputs` |

## 参数参考

| 参数 | 默认值 | 范围 |
|------|--------|------|
| `width` | `2048` | `256-2048`，16 步进 |
| `height` | `2048` | `256-2048`，16 步进 |
| `sampler_preset` | `V4_QUALITY_48` | `V4_QUALITY_48` / `V4_DEFAULT_20` / `V4_TURBO_12` |
| `seed` | `0` | `0-2147483647`，`0` 表示随机 |
| `candidate_count` | `1` | `1-4` |

本地模式中，如果 seed 为 `0`，后端会生成一个随机 base seed；多候选图使用 `base_seed + index`。官方 API v4 文档目前没有暴露请求 seed 参数；官方模式会记录 API 返回的 seed，但不会向官方接口发送未文档化字段。

## 模型与公开排行

Ideogram 4 是 Ideogram 发布的首个开放权重文生图基础模型，官方描述为 **9.3B 参数**、面向设计、文字排版、结构化布局与原生 2K 生成。公开资料中，官方 README / 模型卡强调：

- 在 Design Arena 中是排名最靠前的开放权重设计向图像模型之一。
- 在 ContraLabs 文字排版评测中，Ideogram 4 在设计师偏好和可用于客户工作评分上领先多个强基线。
- 在 LMArena 图像榜单中，Ideogram 是排名靠前的开放权重图像实验室之一。
- 开放权重模型支持结构化 JSON prompt、bbox 布局、色彩调色板和可读文字生成。

参考链接：

- [Ideogram 4 GitHub](https://github.com/ideogram-oss/ideogram4)
- [Ideogram 4 NF4 Hugging Face Model Card](https://huggingface.co/ideogram-ai/ideogram-4-nf4)
- [Ideogram 4 技术博客](https://ideogram.ai/blog/ideogram-4.0/)
- [Generate with Ideogram 4.0 API](https://developer.ideogram.ai/api-reference/api-reference/generate-v4)
- [Magic Prompt v4 API](https://developer.ideogram.ai/api-reference/api-reference/magic-prompt-v4)

## 论文 / 引用

官方仓库给出的引用格式：

```bibtex
@misc{ideogram-4-2026,
  author={Ideogram AI},
  title={{Ideogram 4}},
  year={2026},
  howpublished={\url{https://ideogram.ai/blog/ideogram-4.0/}},
}
```

## 打包与发布

本仓库提供两个 workflow：

| Workflow | 用途 |
|----------|------|
| `.github/workflows/build.yml` | 安装依赖、构建前端、运行 pytest、自检服务 |
| `.github/workflows/release.yml` | 构建 Windows / Linux GPU 便携包并上传 Release |

Release 打包规则：

- Windows：`Ideogram4Generator-Windows-GPU-Portable.zip`
- Linux：`Ideogram4Generator-Linux-GPU-Portable.tar.gz`
- 打包时必须设置仓库 secret `HF_TOKEN`，否则下载权重步骤会失败。
- 便携包会包含前端静态资源、Python 服务、官方运行时依赖和 Hugging Face 权重缓存。

## 开发命令

```bash
npm install
npm run typecheck
npm run build

python -m pip install -r requirements.txt -r requirements-dev.txt
pytest -q
python run.py --self-test
python run.py
```

## License

本仓库代码使用 MIT License。Ideogram 4 权重、官方运行时和模型许可请遵循 Ideogram / Hugging Face 页面中的对应条款。

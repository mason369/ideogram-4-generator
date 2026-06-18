# Ideogram 4 本地图像生成器 / Local CUDA AI Image Generator

<p align="center">
  中文 | <a href="./docs/README.en.md">English</a>
</p>

想试 `Ideogram 4`，又希望图片真的在自己的 NVIDIA 显卡上生成？这个仓库就是 TelkNet 工具的开源本地版：前端界面照着原工具的手感来，后端走 `ideogram-ai/ideogram-4-nf4` 开放权重，Release 里直接打包 Windows / Linux 便携版和模型缓存。解压、运行、打开浏览器，少一点折腾，多一点出图。

项目保留 `prompt / width / height / sampler_preset / seed / candidate_count` 这些 Ideogram 4 常用参数，并把调用链路分得很清楚：

- **本地 CUDA 开放权重生成**：默认模式，不请求官方 Magic Prompt；完整自然语言提示词会先封装成本地 Ideogram 4 JSON，再交给本地 CUDA 运行时生成 PNG。
- **官方 Magic Prompt 提示词优化**：输入 Ideogram API Key 后，只调用官方 `/v1/ideogram-v4/magic-prompt`；拿到 `json_prompt` 后仍然回到本地 CUDA 出图，不调用官方生成图片接口。

> 在线体验：已接入官方提示词优化链路的 TelkNet Ideogram 4 页面在 [https://telknet.cc/tools/ideogram-v4](https://telknet.cc/tools/ideogram-v4)。本仓库是对应的开源本地版，启动后访问 `http://127.0.0.1:7860`。

常见搜索词：`Ideogram 4 本地部署`、`Ideogram 4 CUDA`、`Ideogram 4 Magic Prompt`、`本地文生图`、`open-weight text-to-image`、`local AI image generator`、`Windows Linux portable AI image generation`。

## 截图

| Windows | Linux |
|---------|-------|
| ![Windows 界面](docs/Windows界面.png) | ![Linux 界面](docs/Linux界面.png) |

## 当前能力

- **TelkNet 风格界面**：提示词输入、模型亮点、画布预设、采样预设、候选图数量和生成按钮都放在顺手的位置，第一次打开也不用猜半天。
- **中文默认，英文可切换**：软件界面默认中文，右上角可切到 English；README 也提供中英文两版。
- **Seed 可控也可随机**：`SEED（可选）` 输入框配了骰子按钮；`0` 表示运行时随机，想复现结果就填固定 seed。
- **本地开放权重出图**：通过官方 `ideogram-oss/ideogram4` 推理包调用 `ideogram-ai/ideogram-4-nf4` 或 `fp8` 权重，图片落到 `runtime/outputs/`。
- **官方 Magic Prompt 只管提示词**：官方接口只负责把自然语言扩展成 Ideogram 4 结构化 JSON Prompt，真正的图像生成仍在本地 CUDA 完成。
- **提示词优化可单独跑**：只想看看 Magic Prompt 会把句子改成什么样？点 `仅优化提示词` 即可，不会顺手把显卡点着。
- **参数校验够硬**：尺寸 `256-2048`、16 步进、最大宽高比 `6:1`、候选图 `1-4`、seed `0-2147483647`；不合规就直接报错。
- **失败会明说**：缺 API Key、缺 HF_TOKEN、比例不支持、CUDA 不可用、权重未授权，都会明确报错，不会偷偷换路线。
- **Release 直接带模型**：GitHub Actions 构建 Windows / Linux GPU CUDA NF4 便携包，内置 Ideogram 4 NF4 权重缓存和 CUDA 运行时检查报告，目标机器不需要再手动下载模型。

## 调用链路说明

| 模式 | UI 名称 | 是否接入官方提示词优化 | 输入 | 输出 |
|------|---------|------------------------|------|------|
| `local_plain` | 本地原文提示词 | 否 | 完整自然语言 prompt，本地封装为 Ideogram 4 JSON | 本地 PNG |
| `local_json` | 本地结构化 JSON | 否 | Ideogram 4 JSON caption | 本地 PNG |
| `official_magic` | 官方提示词优化 | 是 | 自然语言 prompt + API Key | 本地 PNG（提示词由官方优化） |

所有生成模式都使用本地 `256-2048`、16 步进画布；本地原文模式会保留完整 prompt 并封装为本地 JSON，官方链路只负责把自然语言 prompt 优化成 Ideogram 4 JSON Prompt，不负责生成图片。

官方模式包含两个动作：

- `仅优化提示词`：只调用 `/v1/ideogram-v4/magic-prompt`，返回结构化 JSON Prompt，不生成图片。
- `生成图像`：先调用 Magic Prompt，再把返回的 JSON Prompt 送入本地 CUDA 运行时。项目不会请求官方 `/v1/ideogram-v4/generate`；Magic Prompt 仍需要 Active API Key。

## 源码拉取与运行

### 1. 拉取源代码

```bash
git clone https://github.com/mason369/ideogram-4-generator.git
cd ideogram-4-generator
```

### 2. 创建虚拟环境并安装 Python 依赖

Windows：

```powershell
python -m venv venv310
venv310\Scripts\python -m pip install --upgrade pip wheel "setuptools<81"
venv310\Scripts\python -m pip install -r requirements.txt
```

Linux / WSL：

```bash
python3 -m venv venv310
source venv310/bin/activate
python -m pip install --upgrade pip wheel "setuptools<81"
python -m pip install -r requirements.txt
```

如果 Ubuntu / WSL 提示缺少 `venv` 模块，先安装：

```bash
sudo apt-get update
sudo apt-get install -y python3.10-venv
```

### 3. 安装前端依赖并构建界面

```bash
npm install
npm run build
```

### 4. 运行仅优化提示词模式（无需本地 GPU，可选）

Windows：

```powershell
venv310\Scripts\python run.py
```

Linux / WSL：

```bash
source venv310/bin/activate
python run.py
```

打开 `http://127.0.0.1:7860`，选择 **官方提示词优化**，点击 **仅优化提示词**。可以在界面输入 Ideogram API Key，也可以设置环境变量 `IDEOGRAM_API_KEY`。

> 这个动作只调用 Magic Prompt，不生成图片。只要点击 **生成图像**，就会进入本地 CUDA 出图流程，需要执行下一节的本地模型准备。

### 5. 源码方式运行本地 CUDA 生成模式

源码运行本地 CUDA 生成需要 CUDA 环境，并已在 Hugging Face 接受 `ideogram-ai/ideogram-4-nf4` 权重许可。该模型为 gated 仓库；匿名访问仅限模型卡等公开说明文件，权重和配置文件下载需要登录认证并完成许可授权。

Windows PowerShell：

```powershell
$env:HF_TOKEN="你的 Hugging Face Token"
venv310\Scripts\python install.py --no-run
venv310\Scripts\python tools\download_ideogram_weights.py --repo-id ideogram-ai/ideogram-4-nf4 --cache-dir models/hf-cache
venv310\Scripts\python run.py
```

Linux / WSL：

```bash
export HF_TOKEN="你的 Hugging Face Token"
source venv310/bin/activate
python install.py --no-run
python tools/download_ideogram_weights.py --repo-id ideogram-ai/ideogram-4-nf4 --cache-dir models/hf-cache
python run.py
```

> 注意：该步骤仅适用于源码运行。Release 便携包由 GitHub Actions 在发布阶段下载并内置模型缓存，运行时不再触发模型下载。

必需条件：

- 已在 Hugging Face 接受 `ideogram-ai/ideogram-4-nf4` 权重许可。
- 环境变量 `HF_TOKEN` 已设置。
- NVIDIA CUDA GPU；`nf4` 是 CUDA 路径。
- 系统内存建议至少 `64 GiB`；程序会用 `IDEOGRAM_MIN_SYSTEM_MEMORY_GB` 检查，低于阈值会显式失败，避免 WSL 或 Windows 进入 OOM。默认 WSL 约 `16 GiB` 内存不足，需要在 `.wslconfig` 中提高 `memory` 后重启 WSL。
- 显存建议 `24 GB+`，适用于较长 Magic Prompt JSON、9:16/高分辨率和 `V4_QUALITY_48`。`16 GB` 显存只适合低分辨率、短提示词和较快采样预设的实验，不作为推荐配置。
- 已安装 `git+https://github.com/ideogram-oss/ideogram4.git`。

### 6. 开发测试命令

```bash
npm run typecheck
npm run build

python -m pip install -r requirements-dev.txt
pytest -q
python run.py --self-test
```

`python run.py --self-test` 会检查 Web 服务和前端静态文件；检测到本地模型缓存时会继续检查本地出图运行时依赖导入。发布包测试会设置 `IDEOGRAM_REQUIRE_MODEL_CACHE=1`，模型缓存缺失时直接失败。

### 常用环境变量

| 变量 | 说明 |
|------|------|
| `IDEOGRAM_API_KEY` | 官方 API Key；UI 输入为空时读取 |
| `HF_TOKEN` | 下载 gated 权重 |
| `IDEOGRAM_QUANTIZATION` | `nf4` 或 `fp8`，默认 `nf4` |
| `IDEOGRAM_DEVICE` | 默认 `cuda` |
| `IDEOGRAM_HF_CACHE` | 指向已下载的 Hugging Face cache |
| `IDEOGRAM_REQUIRE_MODEL_CACHE` | 自检时强制要求本地模型缓存存在，发布包测试使用 |
| `IDEOGRAM_MIN_SYSTEM_MEMORY_GB` | 本地生成前的系统内存下限，默认 `64` |
| `IDEOGRAM_OUTPUT_DIR` | 输出目录，默认 `runtime/outputs` |

## 参数参考

| 参数 | 默认值 | 范围 |
|------|--------|------|
| `width` | `2048` | `256-2048`，16 步进 |
| `height` | `2048` | `256-2048`，16 步进 |
| `sampler_preset` | `V4_QUALITY_48` | `V4_QUALITY_48` / `V4_DEFAULT_20` / `V4_TURBO_12` |
| `seed` | `0` | `0-2147483647`，`0` 表示随机 |
| `candidate_count` | `1` | `1-4` |

如果 seed 为 `0`，后端会生成一个随机 base seed；多候选图使用 `base_seed + index`。官方提示词优化模式同样使用这个本地 seed 规则，因为图片由本地 CUDA 生成，不会向官方出图接口发送 seed 或出图请求。

## 模型与公开资料

Ideogram 4 是 Ideogram 发布的首个开放权重文生图基础模型，规模为 **9.3B 参数**。它的特别之处不只是“能画图”，而是更偏设计工作流：能理解结构化 JSON prompt，能处理多语言文字、布局框、色彩调色板，也支持最高 2K 的本地生成。

公开资料里比较值得看的点有这些：

- **开放权重设计模型**：官方模型卡把 Ideogram 4 定位为面向设计前沿的 open-weight text-to-image model。
- **文字和排版更稳**：官方资料强调它在多语言文字渲染、标识、海报、标题和 UI 文本类任务上表现突出。
- **结构化提示词是核心**：Ideogram 4 训练时就围绕结构化 JSON caption 展开，所以本项目会把自然语言 prompt 包装成本地 JSON；如果使用官方 Magic Prompt，则直接接收官方返回的 `json_prompt`。
- **本地部署更清楚**：源码运行需要 Hugging Face 授权下载权重；Release 便携包已经把模型缓存打进去，适合只想下载软件直接跑的用户。

参考链接：

- [Ideogram 4 GitHub](https://github.com/ideogram-oss/ideogram4)
- [Ideogram 4 NF4 Hugging Face Model Card](https://huggingface.co/ideogram-ai/ideogram-4-nf4)
- [Ideogram 4 技术博客](https://ideogram.ai/blog/ideogram-4.0/)
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
| `.github/workflows/build.yml` | 在 Windows 与 Ubuntu 上安装依赖、构建前端、运行 pytest、自检服务 |
| `.github/workflows/release.yml` | 构建 Windows / Linux GPU CUDA NF4 便携包并上传 Release |

Release 构建规则：

- Windows：`Ideogram4Generator-Windows-GPU-CUDA-NF4-Portable.7z.001` / `.7z.002` ...
- Linux：`Ideogram4Generator-Linux-GPU-CUDA-NF4-Portable.tar.partaa` / `.tar.partab` ...
- Release 构建阶段需要在 GitHub 仓库设置 secret `HF_TOKEN`，并确保该 token 已接受 `ideogram-ai/ideogram-4-nf4` 模型许可；该模型的权重和配置文件不能匿名下载。
- Release workflow 会在 Actions runner 中自动下载 `ideogram-ai/ideogram-4-nf4` 到 `models/hf-cache`，校验缓存非空，再用 PyInstaller 构建便携包。
- `HF_TOKEN` 只作为 GitHub Actions secret 注入下载步骤，不会写入仓库、README、Release Notes 或打包产物；构建前会清理并扫描 Hugging Face cache 中的 token 文件和 token 内容。
- Release 产物包含前端静态资源、Python 服务、开放权重运行时依赖和 Hugging Face 权重缓存；解压运行时不再触发模型下载。
- Release 包内包含 `RUNTIME-CUDA-COMPATIBILITY.txt`，记录本次打包的 PyTorch 版本、CUDA 运行时版本、PyTorch wheel 内置的 `sm_` 架构列表、bitsandbytes CUDA 库和已收集的 CUDA 动态库。
- Release workflow 固定安装 `torch==2.11.0` 的 `cu128` wheel，避免每次发布因 PyTorch 最新版变化导致兼容范围漂移。
- GPU 兼容范围由包内 PyTorch CUDA wheel、bitsandbytes 库和目标机器 NVIDIA 驱动共同决定；便携包不包含 NVIDIA kernel driver，目标机器驱动仍需兼容 CUDA 12.8。
- workflow 会直接生成小于 GitHub Release 单文件上传限制的分卷和 `.sha256` 校验文件。Windows 下载全部 `.7z.00x` 后从 `.7z.001` 解压；Linux 下载全部 `.tar.part*` 后执行 `cat *.tar.part* > package.tar && tar -xf package.tar`。
- workflow 在 build job 内直接上传分卷到 GitHub Release，不通过 Actions artifact 中转。
- 如果 `HF_TOKEN` 缺失、模型许可未接受、CUDA 依赖未收集成功或模型缓存为空，workflow 会显式失败，不上传不完整 GPU 包。

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

本仓库代码使用 MIT License。Ideogram 4 权重、开放权重运行时和模型许可请遵循 Ideogram / Hugging Face 页面中的对应条款。

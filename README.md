# faster-whisper-GUI

    faster-whisper、whisperX，GUI with PySide6

**本仓库**：https://github.com/Syz87/faster-whisper-GUI
**上游原作者**：https://github.com/CheshireCC/faster-whisper-GUI

---

## 这是什么

原作者 [CheshireCC](https://github.com/CheshireCC) 写的 faster-whisper 图形界面。
本仓库是它的改造分支，目标是**把引擎升到最新、把日语字幕这条路彻底走通**。

改造遵循 AGPL-3.0，原作者署名与链接全部保留（见文末「许可证」）。

| 项目 | 上游 v0.8.5 | 本仓库 v0.8.6 |
|---|---|---|
| faster-whisper | 0.10.0（代码却按 1.1 的参数写，装上就报错） | **1.2.1** |
| ctranslate2 | 无版本约束 | **4.9.1**（配 CUDA 12 运行库） |
| 版本号 | 0.8.5 / fw-1.1.0 | **0.8.6 / fw-1.2.1** |
| 各功能页说明 | 只有 tooltip | **七页内置可折叠说明卡**，含模型 CER 对比表 |
| 日译中 | 不支持（Whisper 只能翻英文） | 配套 Sakura-7B 翻译服务 + SRT 翻译脚本 |

---

## 修掉的两个上游 bug

**1. 开 VAD 直接崩**

界面把语音概率阈值写成 `onset`，而 faster-whisper 从 0.10 到 1.2.1 一直叫 `threshold`。
引擎用 `VadOptions(**dict)` 严格展开，多一个键就 `TypeError`。
现在加了参数归一化层（`onset` → `threshold`，并过滤引擎不认识的键）。

**2. large-v3 系列加载报 `Unsupported type: <f8`**

`get_mel_filters()` 返回 float64，ctranslate2 只接受 float32。
已在 `modelLoad.py` 补 `.astype(np.float32)`（上游 master 分支后来才修）。

---

## 快速开始

需要 Python 3.10 ~ 3.12，Windows 推荐 3.11（**安装时记得勾选 Add to PATH**）。

### 省事版：双击两个 bat

```
1. 下载本仓库（git clone 或页面右上角 Code → Download ZIP）
2. 双击 安装环境.bat   ← 自动建虚拟环境、装依赖，会问你要不要装可选组件
3. 双击 下载模型.bat   ← 选一个模型下载，自动放到 models/whisper/
4. 双击 启动.bat       ← 开软件
```

`安装环境.bat` 会说明每一步在干什么，装完提示怎么继续。
`下载模型.bat` 提供三个选项（kotoba / large-v3 / turbo），也可以全下。

### 手动版：一步步来

```bash
git clone https://github.com/Syz87/faster-whisper-GUI.git
cd faster-whisper-GUI

python -m venv .venv
.venv\Scripts\python -m pip install -U pip

# 核心依赖
.venv\Scripts\python -m pip install faster-whisper ctranslate2 PySide6 PySide6-Fluent-Widgets ^
    onnxruntime numpy av soundfile pyaudio nltk webvtt-py joblib opencc-python-reimplemented ^
    requests ffmpeg-python edge-tts huggingface-hub tokenizers

# NVIDIA 显卡需要 CUDA 12 运行库（不用装 CUDA Toolkit，pip 装即可）
.venv\Scripts\python -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cuda-nvrtc-cu12

# 可选：词级对齐 / 说话人分离 / 人声分离
.venv\Scripts\python -m pip install torch torchaudio transformers pandas pyannote.audio
```

然后双击 `启动.bat`（或 `.venv\Scripts\python FasterWhisperGUI.py`）。

**注意**：`torch` 用 pip 默认装的是 CPU 版。对齐和 Demucs 能跑，只是慢一些。
要 GPU 加速得另装 CUDA 版（约 2.5 GB）。

---

## 模型准备

**本仓库不包含任何模型文件**，需要自己下载。
解压后根目录有个 `模型放哪里.txt`，写清了每个模型的下载地址、要放哪个文件夹、以及该选哪个。

两种方式：

### 方式一：软件内在线下载（推荐新手）

打开软件 → 模型参数页 → 选「在线下载模型」→ 填模型名 → 点加载。
会自动走 `HF_ENDPOINT` 指定的镜像下载到 `models/hf-cache`。

### 方式二：手动放到指定目录（推荐，速度快、可控）

把模型文件夹（里面要有 `model.bin`）放到 `models/whisper/<模型名>/`，
软件里选「使用本地模型」并把路径指过去。

**日语识别推荐**（数据来源见下方说明）：

| 模型 | 体积 | 什么时候用 | 下载 |
|---|---|---|---|
| kotoba-whisper-v2.2 | 2.9 GB | **日剧、动画、综艺、vlog** 这类口语视频 | [RoachLin/kotoba-whisper-v2.2-faster](https://huggingface.co/RoachLin/kotoba-whisper-v2.2-faster) |
| large-v3 | 3.1 GB | 有声书、朗读、课程录音；中文英文内容 | [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3) |
| large-v3-turbo | 1.6 GB | 想快、质量能接受略降 | [deepdml/faster-whisper-large-v3-turbo-ct2](https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2) |

**日语 CER 实测对比**（越低越好，来自 kotoba 官方仓库的评测）

| 模型 | 视频口语<br>(ReazonSpeech) | 朗读<br>(JSUT) | 众包口音<br>(CommonVoice8) |
|---|---|---|---|
| **kotoba-whisper-v2.2** | **11.6%** | 8.4% | 9.2% |
| **whisper-large-v3** | 15.1% | **7.1%** | **8.5%** |
| large-v3-turbo（估算） | 约 16% | 约 7.5% | 约 9% |
| whisper-medium | 33.3% | 10.0% | 11.4% |
| whisper-small | 40.8% | 14.2% | 15.7% |

**结论**：kotoba 不是"全面最强"，是**偏科**——只在口语视频类素材上明显赢 large-v3（相对好 23%），
在朗读和口音类上反而输。剪视频用 kotoba，整课程录音用 large-v3。

> 日语没有空格分词，按词算 WER 会虚高到 55%~60%，看 CER 才有意义。

### Demucs 人声分离权重（可选）

点「声乐分离」时，程序会找 `cache/hdemucs_high_trained.pt`。
文件不在就去 `download.pytorch.org` 拉 **319 MB**，国内网络偶尔返回
`HTTP Error 403: Forbidden`，表现为「load model error」。

提前下好放进去就不会触发联网：

```bash
下载模型.bat → 选 4
```

或者手动：

```
https://download.pytorch.org/torchaudio/models/hdemucs_high_trained.pt
→ 存成 cache/hdemucs_high_trained.pt
```

注意别拿 `dl.fbaipublicfiles.com` 上那个 80 MB 的 `955717e8-*.th` 顶替，
那是 demucs 官方包的完整模型对象，torchaudio 读不了（会报
`Unsupported global: GLOBAL demucs.htdemucs.HTDemucs`）。

### 日译中翻译模型（可选）

需要 [llama.cpp](https://github.com/ggml-org/llama.cpp/releases) 的 `llama-server.exe`，
解压到 `tools/llama/`，再把 GGUF 模型放到 `models/translate/`：

| 模型 | 体积 | 显存要求 |
|---|---|---|
| Sakura-7B-Qwen2.5 IQ4_XS | 4.0 GB | 6 GB（推荐） |
| GalTransl-v4-4B Q5_K_S | 2.8 GB | 4 GB |
| nllb-200-distilled-600M | 1.2 GB | CPU 可跑 |

Sakura 是中文社区做的日译中专用模型，纯翻译、不做对话，不会因为内容拒绝翻译。

---

## 日语字幕工作流

```
日语视频
   │
   ├─[可选] Demucs 人声分离 ──→ 人声 wav（BGM 盖过人声时才需要）
   │
   ├─→ faster-whisper 识别 ──→ 日语 SRT
   │
   └─→ whisperX 后处理 ──→ 词级对齐 / 说话人标记（需要时）
                │
                └─→ tools/translate_srt.py + 翻译服务 ──→ 中文 SRT
```

**第一步：提取日语字幕**

1. 双击 `启动.bat`
2. 模型参数页：选本地模型，语言选**日语**（不要用 Auto，日语里的汉字会让自动检测误判成中文）
3. 执行转写页：选视频 → 输出格式 SRT → 开始

**第二步：翻成中文**

1. 双击 `启动翻译服务.bat`，等出现 `listening on http://127.0.0.1:18080`
2. 把日语 SRT 拖到 `tools/translate_srt.py` 上

输出 `xxx.zh.srt`，时间轴原样保留。

---

## 目录结构

```
faster-whisper-GUI/
├─ FasterWhisperGUI.py          启动入口
├─ 安装环境.bat                  一键建虚拟环境 + 装依赖
├─ 下载模型.bat                  一键下载识别模型
├─ 启动.bat                      双击运行（含镜像与缓存设置）
├─ 启动翻译服务.bat              日译中服务
├─ faster_whisper_GUI/          主程序
│  ├─ pageHelp.py               可折叠说明卡组件
│  ├─ helpContent.py            七页说明正文
│  └─ version.py                版本号
├─ whisperx/                    内置的 whisperX（对齐/说话人分离）
├─ tools/
│  └─ translate_srt.py          字幕翻译脚本
├─ models/                       ← 不放模型，需要自己下
│  ├─ whisper/                   识别模型放这里
│  ├─ translate/                 翻译模型放这里
│  └─ hf-cache/                  在线下载缓存
└─ .venv/                       虚拟环境（自行创建）
```

---

## 环境变量

`启动.bat` 里设置，**只对那一个窗口生效**，不改系统环境变量：

| 变量 | 作用 |
|---|---|
| `HF_ENDPOINT=https://hf-mirror.com` | 模型下载镜像，国内直连 HuggingFace 很慢 |
| `HF_HOME=models/hf-cache` | 模型缓存目录，避免占系统盘 |
| `HF_HUB_DISABLE_TELEMETRY=1` | 关闭遥测 |

不需要镜像的话，把 `启动.bat` 里那行删掉即可。

---

## 已知限制

1. **说话人分离需要自己的 HuggingFace Token**
   要先在 `pyannote/speaker-diarization-3.1` 模型页点同意条款，再把 Token 填到软件设置里。
2. **翻译是逐句翻的**，不联系上下文。长对话里人称代词偶尔会飘。
3. **torch 是 CPU 版**，Demucs 分离长音频偏慢（3 分钟歌约 1.5 分钟）。
4. **whisperX 的依赖是延迟加载的**：第一次点「时间戳对齐」要多等十几秒（那才是真正加载模型库的时间）。

---

## 更新

检查更新按钮指向本仓库的 releases：
https://github.com/Syz87/faster-whisper-GUI/releases

上游更新可以这样合并：

```bash
git remote add upstream https://github.com/CheshireCC/faster-whisper-GUI.git
git fetch upstream
git merge upstream/main
```

---

## 许可证

本项目沿用上游的 **GNU Affero General Public License v3.0**，见 [LICENSE](LICENSE)。

按 AGPL-3.0 要求：

- 原始版权归 **CheshireCC** 及各位贡献者所有
- 本仓库的修改同样以 AGPL-3.0 发布
- 通过本软件输出字幕时，文件头会同时标注本仓库与上游仓库地址

---

## 链接

- 上游仓库：[CheshireCC/faster-whisper-GUI](https://github.com/CheshireCC/faster-whisper-GUI)
- [pyside6-fluent-widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [whisperX](https://github.com/m-bain/whisperX)
- [Demucs](https://github.com/facebookresearch/demucs)
- [kotoba-whisper](https://github.com/kotoba-tech/kotoba-whisper)
- [SakuraLLM](https://github.com/SakuraLLM/Sakura-13B-Galgame)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)

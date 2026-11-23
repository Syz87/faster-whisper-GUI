@echo off
chcp 65001 >nul
title faster-whisper-GUI 环境安装

cd /d "%~dp0"

echo ============================================================
echo  faster-whisper-GUI  v0.8.6  环境安装
echo.
echo  这一步会做三件事：
echo    1. 用 Python 创建虚拟环境 .venv
echo    2. 安装运行所需依赖（约 1.5 GB 下载量）
echo    3. 装 NVIDIA CUDA 12 运行库（有 N 卡才需要，约 1.2 GB）
echo.
echo  完成后用 启动.bat 运行软件。
echo  模型需要另外下载，见 README「模型准备」。
echo ============================================================
echo.

REM ---------- 1. 找 Python ----------
set PY=
for %%p in (python.exe) do if not defined PY set PY=%%~$PATH:p
if not defined PY (
    echo [错误] 没找到 python.exe
    echo 请先安装 Python 3.10~3.12（推荐 3.11），安装时勾选 Add to PATH
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 检测 Python 版本...
"%PY%" -c "import sys; v=sys.version_info; print(f'  找到 Python {v.major}.{v.minor}.{v.micro}'); sys.exit(0 if (3,10)<= (v.major,v.minor) <= (3,12) else 1)"
if errorlevel 1 (
    echo [错误] 版本不在 3.10~3.12 范围内，可能装不上依赖
    echo 建议装 Python 3.11
    pause
    exit /b 1
)

REM ---------- 2. 建虚拟环境 ----------
if exist ".venv\Scripts\python.exe" (
    echo [2/4] 虚拟环境已存在，跳过创建
) else (
    echo [2/4] 创建虚拟环境 .venv ...
    "%PY%" -m venv .venv
    if errorlevel 1 (
        echo [错误] 创建失败
        pause
        exit /b 1
    )
)

set VP=.venv\Scripts\python.exe

REM ---------- 3. 装依赖 ----------
echo.
echo [3/4] 安装依赖（耗时较长，请耐心等待）...
echo.

REM 国内用清华源会快很多；在海外可以把 -i 参数删掉
"%VP%" -m pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 goto :pipfail

"%VP%" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ^
    faster-whisper==1.2.1 ctranslate2^>=4.7.2 ^
    PySide6 PySide6-Fluent-Widgets ^
    onnxruntime numpy^<2 av soundfile pyaudio nltk webvtt-py ^
    joblib opencc-python-reimplemented requests ffmpeg-python ^
    edge-tts huggingface-hub tokenizers
if errorlevel 1 goto :pipfail

echo.
echo [3.5/4] 安装 CUDA 运行库（NVIDIA 显卡用，没有 N 卡可以跳过）...
echo         按 Ctrl+C 跳过，装了也不会影响 CPU 模式
"%VP%" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ^
    nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cuda-nvrtc-cu12
if errorlevel 1 (
    echo [提示] CUDA 库安装失败，软件仍可用 CPU 模式运行
)

REM ---------- 4. 可选组件 ----------
echo.
echo ============================================================
echo  核心依赖装好了。
echo.
echo  下面两个是可选功能：
echo    [1] 词级对齐 + 说话人分离 + 人声分离  （需要 PyTorch，约 2.5 GB）
echo    [2] 跳过，只做基础转写
echo.
echo  装了能做什么：字幕时间轴精确到词、区分谁在说话、从音乐里抠人声
echo  不装也能用：正常转写、字幕、翻译
echo ============================================================
set /p OPT="输入 1 或 2 回车: "

if "%OPT%"=="1" (
    echo.
    echo 安装 PyTorch 与相关依赖（这一步很久）...
    "%VP%" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple torch torchaudio
    "%VP%" -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple transformers pandas pyannote.audio
    echo [完成] 可选组件已安装
)

echo.
echo ============================================================
echo  [4/4] 安装完成
echo.
echo  下一步：
echo    1. 下载模型（见 README「模型准备」）
echo       放法：models\whisper\模型名\model.bin
echo    2. 双击 启动.bat
echo ============================================================
pause
exit /b 0

:pipfail
echo.
echo [错误] 依赖安装失败。常见原因：
echo   - 网络问题：重跑一次本脚本即可（已装的会跳过）
echo   - 版本冲突：删掉 .venv 目录重新来
echo   - 缺 Visual C++ 运行库：装 https://aka.ms/vs/17/release/vc_redist.x64.exe
pause
exit /b 1

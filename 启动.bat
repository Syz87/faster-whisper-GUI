@echo off
chcp 65001 >nul
title faster-whisper-GUI v0.8.6 (fw 1.2.1)

cd /d "%~dp0"

REM ============================================================
REM 下面这些变量只对本次启动的进程生效，关闭窗口即失效。
REM 不写系统环境变量，不影响浏览器、代理等其他程序。
REM ============================================================

REM 模型下载镜像（国内直连 HuggingFace 很慢，用镜像）
set HF_ENDPOINT=https://hf-mirror.com

REM 模型缓存目录：放在软件目录下的 models\hf-cache，不占系统盘
set HF_HOME=%~dp0models\hf-cache
set HF_HUB_CACHE=%~dp0models\hf-cache\hub

REM 关掉遥测与符号链接提示
set HF_HUB_DISABLE_TELEMETRY=1
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

REM ffmpeg（可选。放到 tools\ffmpeg\bin 下就会被这里加载）
if exist "%~dp0tools\ffmpeg\bin" set PATH=%~dp0tools\ffmpeg\bin;%PATH%

REM 让 Python 找到项目内的模块
set PYTHONPATH=%~dp0

echo ============================================
echo  faster-whisper-GUI  v0.8.6
echo  引擎: faster-whisper 1.2.1 + ctranslate2 4.x
echo  CUDA : pip 内置 cuBLAS 12 / cuDNN 9
echo  镜像 : %HF_ENDPOINT%   (仅本进程有效)
echo  缓存 : %HF_HOME%
echo ============================================
echo.

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [错误] 没找到虚拟环境 .venv
    echo.
    echo 请先按 README 里的「从源码运行」步骤建好环境：
    echo   python -m venv .venv
    echo   .venv\Scripts\python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" FasterWhisperGUI.py

if errorlevel 1 (
    echo.
    echo [程序异常退出] 错误码: %errorlevel%
    pause
)

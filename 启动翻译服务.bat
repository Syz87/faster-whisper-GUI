@echo off
chcp 65001 >nul
title 翻译服务 - 日译中

cd /d "%~dp0"

REM ============================================================
REM 日译中翻译服务（可选组件）
REM
REM 需要两样东西：
REM   1. llama.cpp 的 llama-server.exe  —— 解压到 tools\llama\
REM   2. 一个 GGUF 格式的翻译模型        —— 放在 models\translate\ 下
REM
REM 推荐模型（按显存选一个）：
REM   6 GB 显存：Sakura-7B-Qwen2.5 IQ4_XS  约 4.0 GB
REM   4 GB 显存：GalTransl-v4-4B Q5_K_S    约 2.8 GB
REM   2 GB 显存：nllb-200-distilled-600M   约 1.2 GB（非 GGUF，用 Python 版）
REM
REM 模型下载见 README「模型准备」一节。
REM ============================================================

set LLAMA=%~dp0tools\llama\llama-server.exe
set MODEL_DIR=%~dp0models\translate

if not exist "%LLAMA%" (
    echo [错误] 没找到 llama-server.exe
    echo 期望位置: %LLAMA%
    echo 请把 llama.cpp 的 Windows 版解压到 tools\llama\
    pause
    exit /b 1
)

REM ---- 自动找模型目录里第一个 .gguf 文件 ----
set MODEL=
for %%f in ("%MODEL_DIR%\*.gguf") do (
    if not defined MODEL set MODEL=%%f
)

if not defined MODEL (
    echo [错误] %MODEL_DIR% 里没有 .gguf 模型文件
    echo 请先下载一个翻译模型放进去，推荐 Sakura-7B IQ4_XS
    pause
    exit /b 1
)

echo ============================================================
echo  翻译服务
echo  模型: %MODEL%
echo  地址: http://127.0.0.1:18080
echo.
echo  看到 "listening on http://127.0.0.1:18080" 即可使用
echo  关闭本窗口即停止服务
echo ============================================================
echo.

"%LLAMA%" -m "%MODEL%" --host 127.0.0.1 --port 18080 -ngl 99 -c 4096 --temp 0.3 --parallel 1

pause

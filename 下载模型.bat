@echo off
chcp 65001 >nul
title 下载识别模型

cd /d "%~dp0"

REM 镜像（国内用这个才快；在海外可以删掉这行）
set HF_ENDPOINT=https://hf-mirror.com
set HF_HUB_DISABLE_TELEMETRY=1

if not exist ".venv\Scripts\python.exe" (
    echo [错误] 还没装环境，请先运行 安装环境.bat
    pause
    exit /b 1
)

echo ============================================================
echo  下载日语识别模型
echo.
echo   [1] kotoba-whisper-v2.2   2.9 GB
echo       日语视频口语最强（日剧 / 动画 / 综艺 / vlog 首选）
echo.
echo   [2] large-v3              3.1 GB
echo       朗读、播客、课程录音更准；中文英文也用这个
echo.
echo   [3] large-v3-turbo        1.6 GB
echo       快 5 倍，质量略降，想省事就选它
echo.
echo   [4] 全部下载              7.6 GB
echo.
echo   模型会放在 models\whisper\ 下
echo ============================================================
set /p OPT="选一个 (1/2/3/4): "

if "%OPT%"=="1" goto :kotoba
if "%OPT%"=="2" goto :v3
if "%OPT%"=="3" goto :turbo
if "%OPT%"=="4" goto :all
echo 输入无效
pause
exit /b 1

:kotoba
echo.
echo 下载 kotoba-whisper-v2.2 ...
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('RoachLin/kotoba-whisper-v2.2-faster', local_dir=r'models\whisper\kotoba-v2.2')"
goto :done

:v3
echo.
echo 下载 large-v3 ...
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-large-v3', local_dir=r'models\whisper\large-v3')"
goto :done

:turbo
echo.
echo 下载 large-v3-turbo ...
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('deepdml/faster-whisper-large-v3-turbo-ct2', local_dir=r'models\whisper\large-v3-turbo')"
goto :done

:all
echo.
echo 下载全部三个模型（约 7.6 GB，会比较久）...
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('RoachLin/kotoba-whisper-v2.2-faster', local_dir=r'models\whisper\kotoba-v2.2')"
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-large-v3', local_dir=r'models\whisper\large-v3')"
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('deepdml/faster-whisper-large-v3-turbo-ct2', local_dir=r'models\whisper\large-v3-turbo')"
goto :done

:done
echo.
echo ============================================================
echo  下载结束
echo.
echo  在软件里这样用：
echo   模型参数页 - 使用本地模型 - 路径指到上面那个文件夹
echo   勾选「使用 v3 模型」（kotoba / large-v3 / turbo 都要勾）
echo   设备选 cuda，精度选 float16
echo ============================================================
pause
exit /b 0

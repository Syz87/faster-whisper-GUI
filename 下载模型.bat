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
echo   [4] Demucs 人声分离权重   319 MB
echo       从音乐/视频里抠人声用，不带它点「声乐分离」会报 403
echo.
echo   [5] 全部下载              7.9 GB
echo.
echo   识别模型放 models\whisper\，Demucs 权重放 cache\
echo ============================================================
set /p OPT="选一个 (1/2/3/4/5): "

if "%OPT%"=="1" goto :kotoba
if "%OPT%"=="2" goto :v3
if "%OPT%"=="3" goto :turbo
if "%OPT%"=="4" goto :demucs
if "%OPT%"=="5" goto :all
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
if not exist "cache" mkdir "cache"
".venv\Scripts\python.exe" -c "import urllib.request,pathlib; p=pathlib.Path('cache/hdemucs_high_trained.pt'); urllib.request.urlretrieve('https://download.pytorch.org/torchaudio/models/hdemucs_high_trained.pt', p)"
goto :done

:demucs
echo.
echo 下载 Demucs 人声分离权重（319 MB）...
if not exist "cache" mkdir "cache"
".venv\Scripts\python.exe" -c "import torch,urllib.request,pathlib; p=pathlib.Path('cache/hdemucs_high_trained.pt'); print('下载中，请稍候...'); urllib.request.urlretrieve('https://download.pytorch.org/torchaudio/models/hdemucs_high_trained.pt', p); print('完成:', p, p.stat().st_size//1048576, 'MB')"
goto :done

:all
echo.
echo 下载全部模型（约 7.9 GB，会比较久）...
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('RoachLin/kotoba-whisper-v2.2-faster', local_dir=r'models\whisper\kotoba-v2.2')"
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-large-v3', local_dir=r'models\whisper\large-v3')"
".venv\Scripts\python.exe" -c "from huggingface_hub import snapshot_download; snapshot_download('deepdml/faster-whisper-large-v3-turbo-ct2', local_dir=r'models\whisper\large-v3-turbo')"
if not exist "cache" mkdir "cache"
".venv\Scripts\python.exe" -c "import urllib.request,pathlib; p=pathlib.Path('cache/hdemucs_high_trained.pt'); urllib.request.urlretrieve('https://download.pytorch.org/torchaudio/models/hdemucs_high_trained.pt', p)"
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
echo.
echo   Demucs 权重已放在 cache\hdemucs_high_trained.pt，
echo   点「声乐分离」就不会再去下载了
echo ============================================================
pause
exit /b 0

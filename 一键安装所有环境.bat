@echo off
setlocal

:: 设置时间限制
set "limit_date=2025-02-25"
for /f "tokens=1-3 delims=- " %%a in ("%date%") do (
    set "current_date=%%c-%%a-%%b"
)

:: 比较日期
if "%current_date%" GTR "%limit_date%" (
    echo 该脚本在2025年2月25日之后无法使用。
    pause
    exit /b 1
)

echo 检查 Python 安装...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 未检测到 Python 安装，请先安装 Python。
    pause
    exit /b 1
)

echo 升级 pip...
python -m pip install --upgrade pip

echo 检查 Tkinter 模块...
python -c "import tkinter" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 当前 Python 环境中没有 Tkinter 模块！
    echo 请确保使用的 Python 已包含 Tkinter 模块（通常默认集成）。
    pause
    exit /b 1
)

echo 安装所需的依赖库...
python -m pip install PyMuPDF Pillow pytesseract tqdm openai pytz

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo 所有依赖库已成功安装！
) ELSE (
    echo.
    echo 安装依赖库时出现错误，请检查 Python 环境设置。
)

pause 
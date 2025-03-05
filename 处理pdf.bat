@echo off
echo 检查 Python 安装...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 未检测到 Python 安装，请先安装 Python。
    pause
    exit /b 1
)

echo 检查 Tkinter 模块...
python -c "import tkinter" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 当前 Python 环境中没有 Tkinter 模块！
    echo 请确保使用的 Python 已包含 Tkinter 模块（通常默认集成）。
    pause
    exit /b 1
)

echo 检查所需的依赖库...
python -c "import fitz, PIL, pytesseract, tqdm" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 检测到缺少依赖库，请先运行 install_env.bat 安装所需库。
    pause
    exit /b 1
)

echo 运行 combined_pdf_to_txt.py...
python combined_pdf_to_txt.py

pause 
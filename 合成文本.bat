@echo off
setlocal enabledelayedexpansion

:: 设置默认参数
set INPUT_DIR=output_reports
set OUTPUT_FILE=merged_report.txt
set ENCODING=utf-8
set PYTHON_CMD=python

:: 检查Python是否可用
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 未找到Python命令，尝试使用py命令...
    set PYTHON_CMD=py
    %PYTHON_CMD% --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo 错误: 未找到Python，请确保Python已安装并添加到PATH中
        exit /b 1
    )
)

:: 检查参数
if "%~1"=="/?" goto :usage
if "%~1"=="-h" goto :usage
if "%~1"=="--help" goto :usage

:: 处理自定义参数
:parse_args
if "%~1"=="" goto :execute
if /i "%~1"=="-i" (
    set INPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--input" (
    set INPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="-o" (
    set OUTPUT_FILE=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--output" (
    set OUTPUT_FILE=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--encoding" (
    set ENCODING=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--no-filename" (
    set NO_FILENAME=--no-filename
    shift
    goto :parse_args
)
echo 警告: 未知参数 %~1，已忽略
shift
goto :parse_args

:execute
echo 开始合并TXT文件...
echo 输入目录: %INPUT_DIR%
echo 输出文件: %OUTPUT_FILE%
echo 文件编码: %ENCODING%

:: 检查Python脚本是否存在
if not exist "%~dp0merge_txt_files.py" (
    echo 错误: 未找到merge_txt_files.py脚本
    exit /b 1
)

:: 执行Python脚本
%PYTHON_CMD% "%~dp0merge_txt_files.py" -i "%INPUT_DIR%" -o "%OUTPUT_FILE%" --encoding "%ENCODING%" %NO_FILENAME%

if %errorlevel% neq 0 (
    echo 错误: 合并文件失败
    exit /b 1
)

echo 文件合并完成！
exit /b 0

:usage
echo 用法: merge_txt_files.bat [选项]
echo 选项:
echo   -i, --input DIR       指定输入目录(默认: output_reports)
echo   -o, --output FILE     指定输出文件(默认: merged_report.txt)
echo   --encoding ENCODING   指定文件编码(默认: utf-8)
echo   --no-filename         不在合并文件中添加原文件名
echo   -h, --help            显示此帮助信息
exit /b 0

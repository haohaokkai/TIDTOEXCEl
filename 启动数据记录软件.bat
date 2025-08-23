@echo off
chcp 65001 >nul
echo 启动数据记录软件...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 检查依赖包
echo 检查依赖包...
python -c "import openpyxl, PIL" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误：依赖包安装失败
        pause
        exit /b 1
    )
)

REM 启动程序
echo 启动程序...
python data_recorder.py

pause

@echo off
chcp 65001 >nul
echo ========================================
echo RFID-TID识别记录软件 - 测试版本
echo ========================================
echo.

echo 功能说明：
echo - 一键自动获取TID和标签号
echo - 自动捕获摄像头图片
echo - 批量数据管理和导出
echo - 自动去重功能
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

echo 检查基础依赖包...
python -c "import tkinter, openpyxl, PIL, cv2" >nul 2>&1
if errorlevel 1 (
    echo 正在安装必需的依赖包...
    pip install openpyxl Pillow opencv-python
    if errorlevel 1 (
        echo 警告：部分依赖包安装失败，程序可能无法正常运行
    )
)

echo.
echo 启动程序...
python data_recorder.py

if errorlevel 1 (
    echo.
    echo 程序异常退出，请检查错误信息
)

pause

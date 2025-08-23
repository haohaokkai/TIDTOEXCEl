@echo off
chcp 65001 >nul
echo ========================================
echo RFID-TID识别记录软件 - 配置版本
echo ========================================
echo.

echo 新功能说明：
echo - 设备配置区域：可选择RFID端口和摄像头
echo - 自动保存配置：选择后自动保存到配置文件
echo - 自动加载配置：程序启动时自动加载保存的配置
echo - 设备检测：自动检测可用的串口和摄像头
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

echo 检查基础依赖包...
python -c "import tkinter, openpyxl, PIL, cv2, serial" >nul 2>&1
if errorlevel 1 (
    echo 正在安装必需的依赖包...
    pip install openpyxl Pillow opencv-python pyserial
    if errorlevel 1 (
        echo 警告：部分依赖包安装失败，程序可能无法正常运行
    )
)

echo.
echo 测试配置功能...
python test_config.py

echo.
echo 启动主程序...
python data_recorder.py

if errorlevel 1 (
    echo.
    echo 程序异常退出，请检查错误信息
)

pause

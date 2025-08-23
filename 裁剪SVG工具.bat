@echo off
chcp 65001 >nul
echo ========================================
echo SVG Logo 裁剪工具
echo ========================================
echo.

echo 请选择裁剪预设:
echo 1. 保留左侧30%% (0 0 30 100)
echo 2. 保留左侧50%% (0 0 50 100)
echo 3. 保留左侧60%% (0 0 60 100)
echo 4. 保留右侧50%% (50 0 100 100)
echo 5. 保留上半部分 (0 0 100 50)
echo 6. 保留下半部分 (0 50 100 100)
echo 7. 保留中心区域 (25 25 75 75)
echo 8. 自定义输入
echo 9. 交互式工具
echo 0. 退出
echo.

set /p choice="请输入选择 (0-9): "

if "%choice%"=="1" (
    echo 执行: 保留左侧30%%
    python crop_svg_simple.py 0 0 30 100
) else if "%choice%"=="2" (
    echo 执行: 保留左侧50%%
    python crop_svg_simple.py 0 0 50 100
) else if "%choice%"=="3" (
    echo 执行: 保留左侧60%%
    python crop_svg_simple.py 0 0 60 100
) else if "%choice%"=="4" (
    echo 执行: 保留右侧50%%
    python crop_svg_simple.py 50 0 100 100
) else if "%choice%"=="5" (
    echo 执行: 保留上半部分
    python crop_svg_simple.py 0 0 100 50
) else if "%choice%"=="6" (
    echo 执行: 保留下半部分
    python crop_svg_simple.py 0 50 100 100
) else if "%choice%"=="7" (
    echo 执行: 保留中心区域
    python crop_svg_simple.py 25 25 75 75
) else if "%choice%"=="8" (
    echo 自定义输入:
    set /p left="左边界百分比 (0-100): "
    set /p top="上边界百分比 (0-100): "
    set /p right="右边界百分比 (0-100): "
    set /p bottom="下边界百分比 (0-100): "
    echo 执行: 左%left%%% 上%top%%% 右%right%%% 下%bottom%%%
    python crop_svg_simple.py %left% %top% %right% %bottom%
) else if "%choice%"=="9" (
    echo 启动交互式工具...
    python crop_svg_logo.py
) else if "%choice%"=="0" (
    echo 退出程序
    exit /b 0
) else (
    echo 无效选择
)

echo.
pause

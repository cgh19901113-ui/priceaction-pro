@echo off
REM Twitter 数据收集 - 一键自动化脚本

echo.
echo ======================================================================
echo Twitter 数据收集器 - 一键自动化
echo ======================================================================
echo.

cd /d "%~dp0"

REM 检查是否已登录
echo [Check] 检查登录状态...
python -c "import os; print('OK' if os.path.exists('browser_profile') else 'NO_PROFILE')" > temp.txt
set /p has_profile=<temp.txt
del temp.txt

if "%has_profile%"=="NO_PROFILE" (
    echo.
    echo [INFO] 首次使用，需要先登录 Twitter
    echo.
    echo 正在打开浏览器...
    python setup_login.py
    echo.
    echo 登录完成后，请重新运行此脚本：
    echo   run.bat
    echo.
    pause
    exit /b
)

REM 自动收集
echo.
echo [Start] 开始全自动收集...
echo.

python run_auto.py

echo.
echo ======================================================================
echo 完成！
echo ======================================================================
echo.
pause

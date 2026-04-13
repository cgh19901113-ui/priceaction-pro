@echo off
cd /d D:\Projects\price-action-saas

:: 检查 git 是否可用
git --version >nul 2>&1
if errorlevel 1 (
    echo Git 未安装，请下载安装：https://git-scm.com/download/win
    pause
    exit /b 1
)

:: 提交代码
git add .
git commit -m "fix: 移除UI标识 + 优化数据不足提示"

:: 检查是否有远程仓库
git remote -v >nul 2>&1
if errorlevel 1 (
    echo 未配置远程仓库，请手动推送
    pause
    exit /b 1
)

:: 推送到远程
git push origin main

echo.
echo 提交完成！
pause
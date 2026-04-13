@echo off
chcp 65001
cls
echo ==========================================
echo  PriceAction-SaaS 更新部署
echo ==========================================
echo.

cd /d D:\Projects\price-action-saas

echo [1/4] 检查 Git 状态...
git status

echo.
echo [2/4] 添加修改...
git add .

echo.
echo [3/4] 提交修改...
git commit -m "fix: 移除UI标识 + 优化数据不足提示"

echo.
echo [4/4] 推送到 GitHub...
git push

echo.
echo ==========================================
echo  提交完成！
echo ==========================================
echo.
echo 修改内容：
echo   - 移除 frontend/index.html 中的 UI 标识
echo   - 优化 backend/main.py 中的数据不足提示
echo.
echo Vercel 将自动部署更新...
echo 请访问 https://vercel.com/dashboard 查看状态
echo.
echo 网站地址: https://priceaction-pro.vercel.app
echo.
pause
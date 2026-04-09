# PriceAction-SaaS 快速部署脚本 (Windows PowerShell)
# 用途：一键部署到 Vercel

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PriceAction-SaaS 快速部署脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "🔍 检查 Python..." -ForegroundColor Yellow
try {
    python --version
    Write-Host "✅ Python 检查通过" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 未安装，请先安装 Python 3.12" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 检查依赖
Write-Host "📦 检查依赖..." -ForegroundColor Yellow
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ requirements.txt 不存在" -ForegroundColor Red
    exit 1
}

pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依赖安装失败" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 依赖安装完成" -ForegroundColor Green
Write-Host ""

# 测试后端
Write-Host "🧪 测试后端..." -ForegroundColor Yellow
Set-Location backend
try {
    python -c "import main; print('Backend OK')"
    Write-Host "✅ 后端测试通过" -ForegroundColor Green
} catch {
    Write-Host "❌ 后端测试失败" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..
Write-Host ""

# 检查 Vercel CLI
Write-Host "🔍 检查 Vercel CLI..." -ForegroundColor Yellow
try {
    vercel --version
    Write-Host "✅ Vercel CLI 检查通过" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Vercel CLI 未安装，正在安装..." -ForegroundColor Yellow
    npm i -g vercel
}
Write-Host ""

# 登录 Vercel
Write-Host "🔑 登录 Vercel..." -ForegroundColor Yellow
try {
    vercel whoami
    Write-Host "✅ Vercel 已登录" -ForegroundColor Green
} catch {
    Write-Host "⚠️  未登录 Vercel，正在登录..." -ForegroundColor Yellow
    vercel login
}
Write-Host ""

# 部署
Write-Host "🚀 开始部署到 Vercel..." -ForegroundColor Cyan
vercel --prod
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 部署失败" -ForegroundColor Red
    exit 1
}
Write-Host ""
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "部署成功！" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "1. 访问生产 URL"
Write-Host "2. 测试 API: /api/analyze?symbol=600519"
Write-Host "3. 检查 Vercel Dashboard"
Write-Host ""

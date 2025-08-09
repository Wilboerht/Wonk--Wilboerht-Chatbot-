# Wonk Chatbot 启动脚本 (PowerShell版本)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Wonk Chatbot 启动脚本" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境是否存在
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ 虚拟环境不存在，请先运行 setup.ps1 进行初始化" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "🔄 激活虚拟环境..." -ForegroundColor Green
& ".venv\Scripts\Activate.ps1"

Write-Host "🚀 启动 Wonk Chatbot..." -ForegroundColor Green
Write-Host ""
Write-Host "📱 启动完成后，请在浏览器中访问：" -ForegroundColor Yellow
Write-Host "   http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 按 Ctrl+C 可以停止服务器" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    python app.py
}
catch {
    Write-Host "❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "👋 Wonk Chatbot 已停止运行" -ForegroundColor Yellow
    Read-Host "按回车键退出"
}

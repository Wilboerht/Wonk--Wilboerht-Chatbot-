@echo off
chcp 65001 >nul
echo ========================================
echo    Wonk Chatbot 一键网络部署工具
echo ========================================
echo.

echo 选择部署方式：
echo 1. Railway (推荐，最简单)
echo 2. Render (稳定可靠)
echo 3. 手动部署指南
echo 4. 退出
echo.

set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" goto railway
if "%choice%"=="2" goto render
if "%choice%"=="3" goto manual
if "%choice%"=="4" goto exit
goto invalid

:railway
echo.
echo 🚀 Railway部署步骤：
echo.
echo 1. 确保代码已上传到GitHub
echo 2. 访问 https://railway.app
echo 3. 使用GitHub账号登录
echo 4. 点击 "New Project" - "Deploy from GitHub repo"
echo 5. 选择你的Wonk项目仓库
echo 6. Railway会自动部署
echo.
echo 💡 提示：部署完成后会获得一个网址，如：
echo    https://your-project.up.railway.app
echo.
echo 是否要打开Railway网站？(y/n)
set /p open_railway=
if /i "%open_railway%"=="y" start https://railway.app
goto end

:render
echo.
echo 🔧 Render部署步骤：
echo.
echo 1. 确保代码已上传到GitHub
echo 2. 访问 https://render.com
echo 3. 注册并连接GitHub账号
echo 4. 点击 "New" - "Web Service"
echo 5. 选择你的GitHub仓库
echo 6. 配置：
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: python app.py
echo    - Environment: Python 3
echo.
echo 是否要打开Render网站？(y/n)
set /p open_render=
if /i "%open_render%"=="y" start https://render.com
goto end

:manual
echo.
echo 📖 手动部署选项：
echo.
echo 1. VPS服务器部署 - 查看 "网络部署指南.md"
echo 2. Docker部署 - 使用 deploy/docker-compose.yml
echo 3. 云服务器部署 - 阿里云、腾讯云等
echo.
echo 是否要打开部署指南？(y/n)
set /p open_guide=
if /i "%open_guide%"=="y" start 网络部署指南.md
goto end

:invalid
echo.
echo ❌ 无效选择，请重新运行脚本
pause
exit /b 1

:end
echo.
echo ✅ 部署信息已显示
echo 📚 详细说明请查看 "网络部署指南.md"
echo.
pause
exit /b 0

:exit
echo.
echo 👋 退出部署工具
exit /b 0

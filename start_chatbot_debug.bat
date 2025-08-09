@echo off
chcp 65001 >nul
echo ========================================
echo    Wonk Chatbot 调试启动脚本
echo ========================================
echo.

echo 🔍 系统信息检查...
echo 当前目录: %CD%
echo Python版本:
python --version
if errorlevel 1 (
    echo ❌ Python 未安装或不在 PATH 中
    echo 请安装 Python 3.8+ 并添加到系统 PATH
    pause
    exit /b 1
)
echo.

echo 🔍 文件检查...
if exist "app.py" (
    echo ✅ app.py 存在
) else (
    echo ❌ app.py 不存在
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

if exist "requirements.txt" (
    echo ✅ requirements.txt 存在
) else (
    echo ❌ requirements.txt 不存在
    pause
    exit /b 1
)

if exist ".venv" (
    echo ✅ .venv 目录存在
) else (
    echo ⚠️  .venv 目录不存在，将创建虚拟环境
    echo 正在创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

if exist ".venv\Scripts\activate.bat" (
    echo ✅ 虚拟环境激活脚本存在
) else (
    echo ❌ 虚拟环境激活脚本不存在
    pause
    exit /b 1
)
echo.

echo 🔄 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 激活虚拟环境失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境激活成功
echo.

echo 🔍 检查 Python 环境...
where python
python --version
echo.

echo 🔍 检查依赖包...
python -c "import flask; print('Flask version:', flask.__version__)" 2>nul
if errorlevel 1 (
    echo ⚠️  Flask 未安装，正在安装依赖...
    pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 安装依赖失败
        echo 尝试使用国内镜像...
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
        if errorlevel 1 (
            echo ❌ 依赖安装失败
            pause
            exit /b 1
        )
    )
    echo ✅ 依赖安装成功
) else (
    echo ✅ Flask 已安装
)
echo.

echo 🔍 检查数据目录...
if not exist "data" (
    echo 📁 创建 data 目录...
    mkdir data
)
echo ✅ 数据目录准备完成
echo.

echo 🚀 启动 Wonk Chatbot...
echo.
echo 📱 启动完成后，请在浏览器中访问：
echo    http://localhost:5000
echo.
echo 💡 按 Ctrl+C 可以停止服务器
echo ========================================
echo.

python app.py

echo.
echo 👋 Wonk Chatbot 已停止运行
pause

@echo off
setlocal enabledelayedexpansion

REM Wonk Chatbot Status Check Script
REM Check service status, environment configuration, port usage, etc.

echo.
echo ================================
echo   Wonk Chatbot Status Check
echo ================================
echo Time: %date% %time%
echo.

REM Check virtual environment
echo [CHECK] Virtual Environment...
if exist ".venv\Scripts\python.exe" (
    echo   + Virtual environment exists: .venv

    REM Check Python version
    for /f "tokens=*" %%i in ('.venv\Scripts\python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   ✓ Python版本: !PYTHON_VERSION!
) else (
    echo   ✗ 虚拟环境不存在
    echo   → 运行 setup.ps1 创建环境
)

:: 检查依赖包
echo.
echo [检查] Python依赖...
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python -c "import uvicorn; print('  ✓ uvicorn:', uvicorn.__version__)" 2>nul || echo   ✗ uvicorn 未安装
    .venv\Scripts\python -c "import fastapi; print('  ✓ fastapi:', fastapi.__version__)" 2>nul || echo   ✗ fastapi 未安装
    .venv\Scripts\python -c "import fastembed; print('  ✓ fastembed:', fastembed.__version__)" 2>nul || echo   ✗ fastembed 未安装
    .venv\Scripts\python -c "import pandas; print('  ✓ pandas:', pandas.__version__)" 2>nul || echo   ✗ pandas 未安装
) else (
    echo   ✗ 无法检查依赖（虚拟环境不存在）
)

:: 检查配置文件
echo.
echo [检查] 配置文件...
if exist "config.yaml" (
    echo   ✓ 主配置文件: config.yaml
) else (
    echo   ⚠ 主配置文件不存在，将使用默认配置
)

if exist ".env" (
    echo   ✓ 环境变量文件: .env
) else (
    echo   ⚠ 环境变量文件不存在
    if exist ".env.example" (
        echo   → 可复制 .env.example 为 .env
    )
)

:: 检查数据目录
echo.
echo [检查] 数据目录...
if exist "data" (
    echo   ✓ 数据目录存在: data\
    
    :: 检查数据库文件
    if exist "data\wonk.db" (
        for %%i in ("data\wonk.db") do set DB_SIZE=%%~zi
        set /a DB_SIZE_KB=!DB_SIZE!/1024
        echo   ✓ 数据库文件: wonk.db (!DB_SIZE_KB! KB)
    ) else (
        echo   ⚠ 数据库文件不存在（首次运行时会自动创建）
    )
    
    :: 检查示例数据
    if exist "data\samples" (
        echo   ✓ 示例数据目录: data\samples\
    )
) else (
    echo   ⚠ 数据目录不存在
)

:: 检查端口占用
echo.
echo [检查] 端口状态...
set PORT_8000_USED=0
for /f "tokens=2,5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    set "PID=%%b"
    echo   端口8000被占用 - PID: !PID!
    
    :: 尝试获取进程名
    for /f "tokens=1" %%c in ('tasklist /fi "pid eq !PID!" /fo csv /nh 2^>nul') do (
        set "PROCESS_NAME=%%c"
        set "PROCESS_NAME=!PROCESS_NAME:"=!"
        echo   进程名: !PROCESS_NAME!
    )
    set PORT_8000_USED=1
)

if !PORT_8000_USED! equ 0 (
    echo   ✓ 端口8000空闲
)

:: 检查服务健康状态
echo.
echo [检查] 服务健康状态...
if !PORT_8000_USED! equ 1 (
    :: 尝试访问健康检查端点
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '  ✓ 服务响应正常' -ForegroundColor Green } else { Write-Host '  ✗ 服务响应异常' -ForegroundColor Red } } catch { Write-Host '  ✗ 服务无响应' -ForegroundColor Red }" 2>nul
    
    :: 检查API文档
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/docs' -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '  ✓ API文档可访问' -ForegroundColor Green } else { Write-Host '  ✗ API文档不可访问' -ForegroundColor Red } } catch { Write-Host '  ✗ API文档不可访问' -ForegroundColor Red }" 2>nul
) else (
    echo   ⚠ 服务未运行
    echo   → 运行 run.bat 启动服务
)

:: 检查系统资源
echo.
echo [检查] 系统资源...
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| findstr /C:"Total Physical Memory"') do (
    set "TOTAL_MEM=%%a"
    echo   总内存:!TOTAL_MEM!
)

for /f "tokens=2 delims=:" %%a in ('systeminfo ^| findstr /C:"Available Physical Memory"') do (
    set "AVAIL_MEM=%%a"
    echo   可用内存:!AVAIL_MEM!
)

:: 显示快速操作提示
echo.
echo ================================
echo   快速操作
echo ================================
echo   启动服务: run.bat
echo   停止服务: stop.bat
echo   配置环境: powershell -ExecutionPolicy Bypass -File setup.ps1
echo   查看日志: 检查控制台输出
echo   API文档: http://127.0.0.1:8000/docs
echo   健康检查: http://127.0.0.1:8000/health
echo.

pause
endlocal

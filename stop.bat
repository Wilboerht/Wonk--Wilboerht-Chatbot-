@echo off
setlocal

:: Wonk Chatbot 停止服务脚本
:: 优雅停止所有相关的Python进程

echo.
echo ================================
echo   Wonk Chatbot 停止服务
echo ================================
echo.

:: 查找相关进程
echo [INFO] 查找Wonk相关进程...

:: 查找uvicorn进程
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr "uvicorn"') do (
    set "PID=%%i"
    set "PID=!PID:"=!"
    echo [INFO] 找到uvicorn进程: PID !PID!
    taskkill /pid !PID! /f >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] 已停止进程 !PID!
    ) else (
        echo [WARNING] 无法停止进程 !PID!
    )
)

:: 查找包含app.main的Python进程
echo [INFO] 查找Python应用进程...
set FOUND_PROCESS=0

for /f "tokens=1,2" %%a in ('wmic process where "name='python.exe'" get processid^,commandline /format:csv ^| findstr "app.main"') do (
    set "PID=%%b"
    if defined PID (
        echo [INFO] 找到应用进程: PID !PID!
        taskkill /pid !PID! /f >nul 2>&1
        if !errorlevel! equ 0 (
            echo [SUCCESS] 已停止进程 !PID!
            set FOUND_PROCESS=1
        ) else (
            echo [WARNING] 无法停止进程 !PID!
        )
    )
)

:: 备用方法：通过端口查找进程
echo [INFO] 检查端口占用...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    set "PID=%%a"
    if defined PID (
        echo [INFO] 找到占用8000端口的进程: PID !PID!
        taskkill /pid !PID! /f >nul 2>&1
        if !errorlevel! equ 0 (
            echo [SUCCESS] 已停止进程 !PID!
            set FOUND_PROCESS=1
        ) else (
            echo [WARNING] 无法停止进程 !PID!
        )
    )
)

:: 等待进程完全停止
echo [INFO] 等待进程完全停止...
timeout /t 2 /nobreak >nul

:: 验证停止结果
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo [SUCCESS] 端口8000已释放
) else (
    echo [WARNING] 端口8000仍被占用
)

if %FOUND_PROCESS% equ 1 (
    echo.
    echo [SUCCESS] Wonk服务已停止
) else (
    echo.
    echo [INFO] 未找到运行中的Wonk服务
)

echo.
echo ================================
echo   停止操作完成
echo ================================
echo.

:: 显示当前状态
echo [INFO] 当前端口状态:
netstat -ano | findstr ":8000" 2>nul
if errorlevel 1 (
    echo   端口8000: 空闲
) else (
    echo   端口8000: 仍被占用
)

echo.
pause
endlocal

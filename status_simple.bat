@echo off
setlocal

REM Simple Wonk Chatbot Status Check

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
    .venv\Scripts\python --version
) else (
    echo   - Virtual environment not found
    echo   - Run setup.ps1 to create environment
)

echo.
REM Check dependencies
echo [CHECK] Python Dependencies...
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python -c "import uvicorn; print('  + uvicorn:', uvicorn.__version__)" 2>nul || echo   - uvicorn not installed
    .venv\Scripts\python -c "import fastapi; print('  + fastapi:', fastapi.__version__)" 2>nul || echo   - fastapi not installed
    .venv\Scripts\python -c "import fastembed; print('  + fastembed:', fastembed.__version__)" 2>nul || echo   - fastembed not installed
) else (
    echo   - Cannot check dependencies (no virtual environment)
)

echo.
REM Check configuration files
echo [CHECK] Configuration Files...
if exist "config.yaml" (
    echo   + Main config file: config.yaml
) else (
    echo   - Main config file not found, will use defaults
)

if exist ".env" (
    echo   + Environment file: .env
) else (
    echo   - Environment file not found
    if exist ".env.example" (
        echo   - You can copy .env.example to .env
    )
)

echo.
REM Check data directory
echo [CHECK] Data Directory...
if exist "data" (
    echo   + Data directory exists: data\
    if exist "data\wonk.db" (
        echo   + Database file exists: wonk.db
    ) else (
        echo   - Database file not found (will be created on first run)
    )
) else (
    echo   - Data directory not found
)

echo.
REM Check port 8000
echo [CHECK] Port Status...
netstat -ano | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo   + Port 8000 is available
    echo   - Service is not running
    echo   - Run run.bat to start service
) else (
    echo   + Port 8000 is in use
    echo   + Service appears to be running
    
    REM Try to check health endpoint
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3; if ($response.StatusCode -eq 200) { Write-Host '  + Service is responding normally' } else { Write-Host '  - Service response abnormal' } } catch { Write-Host '  - Service not responding' }" 2>nul
)

echo.
echo ================================
echo   Quick Actions
echo ================================
echo   Start service: run.bat
echo   Stop service: stop.bat
echo   Setup environment: powershell -ExecutionPolicy Bypass -File setup.ps1
echo   API docs: http://127.0.0.1:8000/docs
echo   Health check: http://127.0.0.1:8000/health
echo.

pause
endlocal

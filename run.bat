@echo off
setlocal enabledelayedexpansion

REM Wonk Chatbot Startup Script
REM Support multiple startup modes and parameters

REM Default configuration
set HOST=127.0.0.1
set PORT=8000
set MODE=dev
set RELOAD=--reload

REM Parse command line arguments
:parse_args
if "%1"=="" goto start_service
if "%1"=="--prod" (
    set MODE=prod
    set RELOAD=
    shift
    goto parse_args
)
if "%1"=="--dev" (
    set MODE=dev
    set RELOAD=--reload
    shift
    goto parse_args
)
if "%1"=="--port" (
    set PORT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--host" (
    set HOST=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--help" (
    goto show_help
)
if "%1"=="-h" (
    goto show_help
)
shift
goto parse_args

:show_help
echo.
echo Wonk Chatbot Startup Script
echo.
echo Usage: run.bat [options]
echo.
echo Options:
echo   --dev          Development mode (default, enable hot reload)
echo   --prod         Production mode (disable hot reload, optimize performance)
echo   --host HOST    Bind host address (default: 127.0.0.1)
echo   --port PORT    Bind port (default: 8000)
echo   --help, -h     Show this help message
echo.
echo Examples:
echo   run.bat                    # Start in development mode
echo   run.bat --prod             # Start in production mode
echo   run.bat --port 8080        # Specify port
echo   run.bat --host 0.0.0.0     # Listen on all interfaces
echo.
goto end

:start_service
REM Check virtual environment
set "PYEXE=.venv\Scripts\python.exe"
if not exist "%PYEXE%" (
    echo [ERROR] Virtual environment not found, please run setup.ps1 first
    echo.
    echo Quick setup: powershell -ExecutionPolicy Bypass -File setup.ps1
    echo.
    echo Or manual setup:
    echo   1. py -m venv .venv
    echo   2. .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    goto end
)

REM Check dependencies
echo [INFO] Checking environment...
"%PYEXE%" -c "import uvicorn, fastapi" 2>nul
if errorlevel 1 (
    echo [ERROR] Missing dependencies, please run: .venv\Scripts\pip install -r requirements.txt
    pause
    goto end
)

REM Display startup information
echo.
echo ================================
echo   Wonk Chatbot Starting...
echo ================================
echo Mode: %MODE%
echo Address: http://%HOST%:%PORT%
echo Time: %date% %time%
if "%MODE%"=="dev" (
    echo Hot Reload: Enabled
) else (
    echo Hot Reload: Disabled
)
echo ================================
echo.

REM Start service
echo [INFO] Starting service...
"%PYEXE%" -m uvicorn app.main:app --host %HOST% --port %PORT% %RELOAD%

:end
if "%MODE%"=="dev" (
    echo.
    echo [INFO] Service stopped
    pause
)
endlocal

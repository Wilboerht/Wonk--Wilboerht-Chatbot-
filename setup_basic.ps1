# Wonk Chatbot Basic Setup Script
# Simple and compatible version

param(
    [switch]$Force,
    [switch]$SkipDeps
)

Write-Host "=== Wonk Chatbot Environment Setup ===" -ForegroundColor Magenta
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: requirements.txt not found" -ForegroundColor Red
    Write-Host "Please run this script in the project root directory" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Cyan
$pythonFound = $false
$pythonCmd = ""

# Try python command
try {
    $version = python --version 2>$null
    if ($version -and $version -match "Python 3\.(\d+)") {
        $minor = [int]$matches[1]
        if ($minor -ge 8) {
            Write-Host "Found Python: $version" -ForegroundColor Green
            $pythonFound = $true
            $pythonCmd = "python"
        }
    }
} catch {
    # Python command not found
}

# Try py command if python not found
if (-not $pythonFound) {
    try {
        $version = py --version 2>$null
        if ($version -and $version -match "Python 3\.(\d+)") {
            $minor = [int]$matches[1]
            if ($minor -ge 8) {
                Write-Host "Found Python: $version" -ForegroundColor Green
                $pythonFound = $true
                $pythonCmd = "py"
            }
        }
    } catch {
        # py command not found
    }
}

if (-not $pythonFound) {
    Write-Host "ERROR: Python 3.8+ not found" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Check virtual environment
$venvPath = ".venv"
if (Test-Path $venvPath) {
    if ($Force) {
        Write-Host "Force mode: removing existing virtual environment" -ForegroundColor Yellow
        Remove-Item $venvPath -Recurse -Force
    } else {
        Write-Host "Virtual environment already exists: $venvPath" -ForegroundColor Green
        $recreate = Read-Host "Recreate virtual environment? (y/N)"
        if ($recreate -eq "y" -or $recreate -eq "Y") {
            Remove-Item $venvPath -Recurse -Force
        } else {
            Write-Host "Skipping virtual environment creation" -ForegroundColor Cyan
            $skipVenv = $true
        }
    }
}

# Create virtual environment
if (-not $skipVenv) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    try {
        if ($pythonCmd -eq "python") {
            python -m venv $venvPath
        } else {
            py -m venv $venvPath
        }
        Write-Host "Virtual environment created successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}

# Install dependencies
if (-not $SkipDeps) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    $pipPath = ".venv\Scripts\pip.exe"
    
    if (Test-Path $pipPath) {
        try {
            # Upgrade pip
            & $pipPath install --upgrade pip
            
            # Install dependencies
            & $pipPath install -r requirements.txt
            Write-Host "Dependencies installed successfully" -ForegroundColor Green
        } catch {
            Write-Host "WARNING: Failed to install some dependencies" -ForegroundColor Yellow
            Write-Host "You can manually run: .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
        }
    } else {
        Write-Host "ERROR: pip not found in virtual environment" -ForegroundColor Red
    }
}

# Check configuration files
Write-Host "Checking configuration files..." -ForegroundColor Cyan
if (-not (Test-Path "config.yaml")) {
    Write-Host "config.yaml not found, will use default configuration" -ForegroundColor Yellow
} else {
    Write-Host "Configuration file exists: config.yaml" -ForegroundColor Green
}

# Create .env file
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Creating environment variables file..." -ForegroundColor Cyan
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file, please modify as needed" -ForegroundColor Green
    } else {
        Write-Host ".env.example file not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "Environment variables file exists: .env" -ForegroundColor Green
}

# Create data directory
$dataDir = "data"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
    Write-Host "Created data directory: $dataDir" -ForegroundColor Green
}

# Completion message
Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "Environment setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start service: .\run.bat" -ForegroundColor White
Write-Host "  2. Check status: .\status_simple.bat" -ForegroundColor White
Write-Host "  3. Access service: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  4. API documentation: http://127.0.0.1:8000/docs" -ForegroundColor White

if (Test-Path ".env") {
    Write-Host ""
    Write-Host "Security reminder:" -ForegroundColor Yellow
    Write-Host "  - Please modify WONK_ADMIN_TOKEN in .env file to a secure password" -ForegroundColor Yellow
}

Write-Host ""

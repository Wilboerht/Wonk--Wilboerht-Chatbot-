# Wonk Chatbot Simple Setup Script
# Automatically detect Python, create virtual environment, install dependencies

param(
    [switch]$Force,
    [switch]$Verbose,
    [switch]$SkipDeps
)

# Set error handling
$ErrorActionPreference = "Stop"

# Color output functions
function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Error { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }

# Check Python installation
function Test-Python {
    $pythonCommands = @("python", "py")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = Invoke-Expression "$cmd --version" 2>$null
            if ($version -match "Python (\d+)\.(\d+)") {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]
                if ($major -eq 3 -and $minor -ge 8) {
                    Write-Success "Found Python: $version (command: $cmd)"
                    return $cmd
                } else {
                    Write-Warning "Python version too old: $version (need Python 3.8+)"
                }
            }
        } catch {
            # Command not found, try next
        }
    }
    return $null
}

# Main setup process
function Main {
    Write-Host "=== Wonk Chatbot Environment Setup ===" -ForegroundColor Magenta
    Write-Info "Starting environment check and configuration..."
    
    # Check current directory
    if (-not (Test-Path "requirements.txt")) {
        Write-Error "requirements.txt not found, please run this script in project root directory"
        exit 1
    }
    
    # Check Python
    Write-Info "Checking Python installation..."
    $pythonCmd = Test-Python
    if (-not $pythonCmd) {
        Write-Error "Suitable Python version not found (need Python 3.8+)"
        Write-Info "Please visit https://www.python.org/downloads/ to download and install Python"
        Write-Info "Make sure to check 'Add Python to PATH' during installation"
        exit 1
    }
    
    # Check virtual environment
    $venvPath = ".venv"
    if (Test-Path $venvPath) {
        if ($Force) {
            Write-Warning "Force mode: removing existing virtual environment"
            Remove-Item $venvPath -Recurse -Force
        } else {
            Write-Success "Virtual environment already exists: $venvPath"
            $recreate = Read-Host "Recreate virtual environment? (y/N)"
            if ($recreate -eq "y" -or $recreate -eq "Y") {
                Remove-Item $venvPath -Recurse -Force
            } else {
                Write-Info "Skipping virtual environment creation"
                $skipVenv = $true
            }
        }
    }
    
    # Create virtual environment
    if (-not $skipVenv) {
        Write-Info "Creating virtual environment..."
        try {
            $createCmd = "$pythonCmd -m venv $venvPath"
            Invoke-Expression $createCmd
            Write-Success "Virtual environment created successfully"
        } catch {
            Write-Error "Failed to create virtual environment: $_"
            exit 1
        }
    }
    
    # Install dependencies
    $pipPath = Join-Path $venvPath "Scripts\pip.exe"
    
    if (-not $SkipDeps) {
        Write-Info "Installing Python dependencies..."
        try {
            # Upgrade pip
            $upgradeCmd = "$pipPath install --upgrade pip"
            Invoke-Expression $upgradeCmd

            # Install dependencies
            $installCmd = "$pipPath install -r requirements.txt"
            Invoke-Expression $installCmd
            Write-Success "Dependencies installed successfully"
        } catch {
            Write-Error "Failed to install dependencies: $_"
            Write-Info "You can manually run later: .venv\Scripts\pip install -r requirements.txt"
        }
    }
    
    # Check configuration files
    Write-Info "Checking configuration files..."
    if (-not (Test-Path "config.yaml")) {
        Write-Warning "config.yaml not found, will use default configuration"
    } else {
        Write-Success "Configuration file exists: config.yaml"
    }
    
    # Check environment variables file
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-Info "Creating environment variables file..."
            Copy-Item ".env.example" ".env"
            Write-Success "Created .env file, please modify as needed"
        } else {
            Write-Warning ".env.example file not found"
        }
    } else {
        Write-Success "Environment variables file exists: .env"
    }
    
    # Create data directory
    $dataDir = "data"
    if (-not (Test-Path $dataDir)) {
        New-Item -ItemType Directory -Path $dataDir | Out-Null
        Write-Success "Created data directory: $dataDir"
    }
    
    # Completion message
    Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
    Write-Success "Environment setup completed successfully!"
    Write-Info "`nNext steps:"
    Write-Host "  1. Start service: .\run.bat" -ForegroundColor White
    Write-Host "  2. Or manual start: .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000" -ForegroundColor White
    Write-Host "  3. Access service: http://127.0.0.1:8000" -ForegroundColor White
    Write-Host "  4. API documentation: http://127.0.0.1:8000/docs" -ForegroundColor White
    
    if (Test-Path ".env") {
        Write-Info "`nSecurity reminder:"
        Write-Host "  - Please modify WONK_ADMIN_TOKEN in .env file to a secure password" -ForegroundColor Yellow
        Write-Host "  - Read docs/运行与维护.md before production deployment" -ForegroundColor Yellow
    }
}

# Script entry point
try {
    Main
} catch {
    Write-Error "Error occurred during setup: $_"
    Write-Info "Please check the error message and retry, or configure environment manually"
    exit 1
}

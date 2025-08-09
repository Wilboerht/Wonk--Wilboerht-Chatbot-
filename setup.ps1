# Wonk Chatbot 一键环境配置脚本
# 自动检测Python、创建虚拟环境、安装依赖

param(
    [switch]$Force,
    [switch]$Verbose,
    [switch]$SkipDeps
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✓ $Message" "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput "✗ $Message" "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠ $Message" "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ $Message" "Cyan" }

# 检查管理员权限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查Python安装
function Test-Python {
    $pythonCommands = @("python", "py")
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>$null
            if ($version -match "Python (\d+)\.(\d+)") {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]
                if ($major -eq 3 -and $minor -ge 8) {
                    Write-Success "找到Python: $version (命令: $cmd)"
                    return $cmd
                } else {
                    Write-Warning "Python版本过低: $version (需要Python 3.8+)"
                }
            }
        } catch {
            # 命令不存在，继续尝试下一个
        }
    }
    return $null
}

# 主要设置流程
function Main {
    Write-ColorOutput "=== Wonk Chatbot 环境配置 ===" "Magenta"
    Write-Info "开始检查和配置环境..."
    
    # 检查当前目录
    if (-not (Test-Path "requirements.txt")) {
        Write-Error "未找到 requirements.txt，请在项目根目录运行此脚本"
        exit 1
    }
    
    # 检查Python
    Write-Info "检查Python安装..."
    $pythonCmd = Test-Python
    if (-not $pythonCmd) {
        Write-Error "未找到合适的Python版本 (需要Python 3.8+)"
        Write-Info "请访问 https://www.python.org/downloads/ 下载并安装Python"
        Write-Info "安装时请勾选 'Add Python to PATH'"
        exit 1
    }
    
    # 检查虚拟环境
    $venvPath = ".venv"
    if (Test-Path $venvPath) {
        if ($Force) {
            Write-Warning "强制模式：删除现有虚拟环境"
            Remove-Item $venvPath -Recurse -Force
        } else {
            Write-Success "虚拟环境已存在: $venvPath"
            $recreate = Read-Host "是否重新创建虚拟环境? (y/N)"
            if ($recreate -eq "y" -or $recreate -eq "Y") {
                Remove-Item $venvPath -Recurse -Force
            } else {
                Write-Info "跳过虚拟环境创建"
                $skipVenv = $true
            }
        }
    }
    
    # 创建虚拟环境
    if (-not $skipVenv) {
        Write-Info "创建虚拟环境..."
        try {
            & $pythonCmd -m venv $venvPath
            Write-Success "虚拟环境创建成功"
        } catch {
            Write-Error "虚拟环境创建失败: $_"
            exit 1
        }
    }
    
    # 激活虚拟环境并安装依赖
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    $pipPath = Join-Path $venvPath "Scripts\pip.exe"
    
    if (-not (Test-Path $activateScript)) {
        Write-Error "虚拟环境激活脚本不存在"
        exit 1
    }
    
    if (-not $SkipDeps) {
        Write-Info "安装Python依赖..."
        try {
            # 升级pip
            & $pipPath install --upgrade pip
            
            # 安装依赖
            & $pipPath install -r requirements.txt
            Write-Success "依赖安装完成"
        } catch {
            Write-Error "依赖安装失败: $_"
            Write-Info "你可以稍后手动运行: .venv\Scripts\pip install -r requirements.txt"
        }
    }
    
    # 检查配置文件
    Write-Info "检查配置文件..."
    if (-not (Test-Path "config.yaml")) {
        Write-Warning "未找到 config.yaml，将使用默认配置"
    } else {
        Write-Success "配置文件存在: config.yaml"
    }
    
    # 检查环境变量文件
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-Info "创建环境变量文件..."
            Copy-Item ".env.example" ".env"
            Write-Success "已创建 .env 文件，请根据需要修改"
        } else {
            Write-Warning "未找到 .env.example 文件"
        }
    } else {
        Write-Success "环境变量文件存在: .env"
    }
    
    # 创建数据目录
    $dataDir = "data"
    if (-not (Test-Path $dataDir)) {
        New-Item -ItemType Directory -Path $dataDir | Out-Null
        Write-Success "创建数据目录: $dataDir"
    }
    
    # 完成提示
    Write-ColorOutput "`n=== 配置完成 ===" "Green"
    Write-Success "环境配置成功完成！"
    Write-Info "`n下一步操作："
    Write-ColorOutput "  1. 启动服务: .\run.bat" "White"
    Write-ColorOutput "  2. 或者手动启动: .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000" "White"
    Write-ColorOutput "  3. 访问服务: http://127.0.0.1:8000" "White"
    Write-ColorOutput "  4. API文档: http://127.0.0.1:8000/docs" "White"
    
    if (Test-Path ".env") {
        Write-Info "`n安全提醒："
        Write-ColorOutput "  - 请修改 .env 文件中的 WONK_ADMIN_TOKEN 为安全密码" "Yellow"
        Write-ColorOutput "  - 生产环境部署前请阅读 docs/运行与维护.md" "Yellow"
    }
}

# 脚本入口
try {
    Main
} catch {
    Write-Error "配置过程中发生错误: $_"
    Write-Info "请检查错误信息并重试，或手动配置环境"
    exit 1
}

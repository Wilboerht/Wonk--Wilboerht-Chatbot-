#!/bin/bash
# Wonk Chatbot 云服务器部署脚本
# 适用于 Ubuntu/Debian 系统

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 Wonk Chatbot 云服务器部署脚本"
echo "=========================================="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_info "检测到root用户，继续执行..."
    else
        log_error "请使用root用户执行此脚本"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    apt update && apt upgrade -y
    log_info "系统更新完成"
}

# 安装基础软件
install_basics() {
    log_info "安装基础软件包..."
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        nginx \
        ufw \
        curl \
        wget \
        unzip \
        htop \
        tree
    log_info "基础软件安装完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 5000/tcp  # Flask应用端口
    ufw --force enable
    log_info "防火墙配置完成"
}

# 创建应用用户
create_app_user() {
    log_info "创建应用用户..."
    if id "wonk" &>/dev/null; then
        log_warn "用户 wonk 已存在"
    else
        useradd -m -s /bin/bash wonk
        log_info "用户 wonk 创建完成"
    fi
}

# 创建应用目录
setup_app_directory() {
    log_info "设置应用目录..."
    mkdir -p /opt/wonk-chatbot
    chown wonk:wonk /opt/wonk-chatbot
    log_info "应用目录创建完成"
}

# 主函数
main() {
    echo "开始服务器环境配置..."
    echo
    
    check_root
    update_system
    install_basics
    setup_firewall
    create_app_user
    setup_app_directory
    
    echo
    log_info "=========================================="
    log_info "🎉 服务器基础环境配置完成！"
    log_info "=========================================="
    echo
    log_info "下一步："
    log_info "1. 上传项目代码到 /opt/wonk-chatbot/"
    log_info "2. 运行应用部署脚本"
    log_info "3. 配置Nginx（可选）"
    echo
    log_info "服务器信息："
    log_info "- Python版本: $(python3 --version)"
    log_info "- 应用目录: /opt/wonk-chatbot"
    log_info "- 应用用户: wonk"
    log_info "- 防火墙状态: $(ufw status | head -1)"
    echo
}

# 执行主函数
main "$@"

#!/bin/bash
# Wonk Chatbot 应用部署脚本

set -e

echo "=========================================="
echo "📦 Wonk Chatbot 应用部署脚本"
echo "=========================================="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
APP_DIR="/opt/wonk-chatbot"
APP_USER="wonk"
SERVICE_NAME="wonk-chatbot"

# 检查是否为root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用root用户执行此脚本"
        exit 1
    fi
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    cd $APP_DIR
    
    # 创建虚拟环境
    sudo -u $APP_USER python3 -m venv venv
    
    # 激活虚拟环境并安装依赖
    sudo -u $APP_USER bash -c "
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    "
    
    log_info "Python依赖安装完成"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Wonk Chatbot
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=FLASK_ENV=production
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    log_info "systemd服务创建完成"
}

# 创建数据目录
setup_data_directory() {
    log_info "设置数据目录..."
    mkdir -p $APP_DIR/data
    chown -R $APP_USER:$APP_USER $APP_DIR/data
    log_info "数据目录设置完成"
}

# 启动服务
start_service() {
    log_info "启动Wonk Chatbot服务..."
    systemctl start $SERVICE_NAME
    sleep 3
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_info "✅ 服务启动成功！"
    else
        log_error "❌ 服务启动失败"
        log_error "查看日志: journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
}

# 检查服务状态
check_service() {
    log_info "检查服务状态..."
    systemctl status $SERVICE_NAME --no-pager
    
    log_info "测试HTTP连接..."
    sleep 2
    if curl -f http://localhost:5000/ > /dev/null 2>&1; then
        log_info "✅ HTTP服务正常"
    else
        log_warn "⚠️ HTTP服务可能未正常启动"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo
    log_info "=========================================="
    log_info "🎉 应用部署完成！"
    log_info "=========================================="
    echo
    log_info "访问信息："
    log_info "- 内网访问: http://localhost:5000"
    log_info "- 公网访问: http://120.55.160.247:5000"
    echo
    log_info "服务管理命令："
    log_info "- 查看状态: systemctl status $SERVICE_NAME"
    log_info "- 启动服务: systemctl start $SERVICE_NAME"
    log_info "- 停止服务: systemctl stop $SERVICE_NAME"
    log_info "- 重启服务: systemctl restart $SERVICE_NAME"
    log_info "- 查看日志: journalctl -u $SERVICE_NAME -f"
    echo
    log_info "文件位置："
    log_info "- 应用目录: $APP_DIR"
    log_info "- 数据库文件: $APP_DIR/data/database.db"
    log_info "- 日志文件: journalctl -u $SERVICE_NAME"
    echo
}

# 主函数
main() {
    check_root
    
    if [ ! -d "$APP_DIR" ] || [ ! -f "$APP_DIR/app.py" ]; then
        log_error "应用代码未找到，请先上传代码到 $APP_DIR"
        exit 1
    fi
    
    install_dependencies
    setup_data_directory
    create_systemd_service
    start_service
    check_service
    show_deployment_info
}

main "$@"

#!/bin/bash
# Nginx配置脚本

set -e

echo "=========================================="
echo "🌐 Nginx反向代理配置脚本"
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
SERVER_IP="120.55.160.247"
DOMAIN_NAME=""  # 如果有域名，在这里设置

# 检查是否为root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用root用户执行此脚本"
        exit 1
    fi
}

# 询问域名配置
ask_domain() {
    echo "是否要配置域名？"
    echo "1. 只使用IP访问 (http://120.55.160.247)"
    echo "2. 配置域名访问 (需要域名解析到此IP)"
    read -p "请选择 (1/2): " choice
    
    if [ "$choice" = "2" ]; then
        read -p "请输入你的域名 (例如: chat.example.com): " DOMAIN_NAME
        if [ -z "$DOMAIN_NAME" ]; then
            log_warn "未输入域名，将使用IP访问"
            DOMAIN_NAME=""
        fi
    fi
}

# 创建Nginx配置
create_nginx_config() {
    log_info "创建Nginx配置..."
    
    if [ -n "$DOMAIN_NAME" ]; then
        # 有域名的配置
        cat > /etc/nginx/sites-available/wonk-chatbot << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME $SERVER_IP;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 静态文件
    location /static/ {
        proxy_pass http://127.0.0.1:5000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 主应用
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
    else
        # 只有IP的配置
        cat > /etc/nginx/sites-available/wonk-chatbot << EOF
server {
    listen 80 default_server;
    server_name $SERVER_IP _;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 静态文件
    location /static/ {
        proxy_pass http://127.0.0.1:5000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 主应用
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
    fi
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/wonk-chatbot /etc/nginx/sites-enabled/
    
    # 删除默认站点
    rm -f /etc/nginx/sites-enabled/default
    
    log_info "Nginx配置创建完成"
}

# 测试并重启Nginx
restart_nginx() {
    log_info "测试Nginx配置..."
    nginx -t
    
    log_info "重启Nginx..."
    systemctl restart nginx
    systemctl enable nginx
    
    log_info "Nginx配置完成"
}

# 显示访问信息
show_access_info() {
    echo
    log_info "=========================================="
    log_info "🎉 Nginx配置完成！"
    log_info "=========================================="
    echo
    log_info "访问地址："
    if [ -n "$DOMAIN_NAME" ]; then
        log_info "- 域名访问: http://$DOMAIN_NAME"
    fi
    log_info "- IP访问: http://$SERVER_IP"
    echo
    log_info "注意事项："
    log_info "- 确保防火墙已开放80端口"
    log_info "- 如果使用域名，确保DNS解析正确"
    log_info "- 可以考虑配置SSL证书(HTTPS)"
    echo
}

# 主函数
main() {
    check_root
    ask_domain
    create_nginx_config
    restart_nginx
    show_access_info
}

main "$@"

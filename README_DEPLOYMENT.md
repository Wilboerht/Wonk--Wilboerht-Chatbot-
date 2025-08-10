# Wonk Chatbot 部署指南

## 🚀 快速开始

### 本地开发部署

#### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/Wilboerht/Wonk--Wilboerht-Chatbot-.git
cd Wonk--Wilboerht-Chatbot-

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 启动服务
```bash
python app.py
```

#### 4. 访问服务
- 主页：http://localhost:5000
- 聊天界面：http://localhost:5000

## 🌐 云服务器部署

### 完整部署指南
详见 [服务器完整配置记录.md](服务器完整配置记录.md)

### 快速部署步骤
1. **连接服务器**
   ```bash
   ssh root@your-server-ip
   ```

2. **下载项目**
   ```bash
   cd /tmp
   yum install -y git
   git clone https://github.com/Wilboerht/Wonk--Wilboerht-Chatbot-.git
   ```

3. **执行部署脚本**
   ```bash
   cd Wonk--Wilboerht-Chatbot-/deploy
   chmod +x *.sh
   ./server_setup_alinux.sh    # 配置环境
   ./deploy_app.sh             # 部署应用
   ./setup_nginx.sh            # 配置Nginx
   ```

4. **配置SSL证书**
   ```bash
   yum install -y certbot python3-certbot-nginx
   certbot --nginx -d your-domain.com
   ```

## 🔧 配置说明

### 应用配置
- **主应用**: `app.py` (Flask)
- **端口**: 5000 (内部), 80/443 (外部)
- **数据库**: SQLite (`data/database.db`)
- **日志**: systemd journal

### 环境变量
```bash
# 生产环境
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
```

## 🔐 安全配置

### 生产环境安全
```bash
# 修改Flask密钥
# 编辑 app.py 中的 secret_key

# 配置防火墙
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload

# SSL证书配置
certbot --nginx -d your-domain.com
```

## 📊 数据管理

### 数据库备份
```bash
# 备份数据库
cp /opt/wonk-chatbot/data/database.db /opt/wonk-chatbot/data/database_backup_$(date +%Y%m%d).db

# 定期备份（添加到crontab）
echo "0 2 * * * cp /opt/wonk-chatbot/data/database.db /opt/wonk-chatbot/data/database_backup_\$(date +\%Y\%m\%d).db" | crontab -
```

## 🔍 状态检查

### 本地开发
```bash
# 检查Python版本
python --version

# 检查虚拟环境
which python  # Linux/Mac
where python   # Windows

# 检查依赖
pip list
```

### 服务器部署
```bash
# 检查服务状态
systemctl status wonk-chatbot

# 检查端口监听
ss -tlnp | grep 5000

# 检查日志
journalctl -u wonk-chatbot -n 20
```

## 🛠️ 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 查看详细错误
   journalctl -u wonk-chatbot -f

   # 手动测试
   cd /opt/wonk-chatbot
   source venv/bin/activate
   python app.py
   ```

2. **端口访问问题**
   ```bash
   # 检查防火墙
   firewall-cmd --list-ports

   # 开放端口
   firewall-cmd --permanent --add-port=5000/tcp
   firewall-cmd --reload
   ```

3. **SSL证书问题**
   ```bash
   # 检查证书状态
   certbot certificates

   # 手动续期
   certbot renew
   ```

## 🌐 生产部署

### 安全检查清单
- [ ] 修改Flask应用密钥
- [ ] 配置HTTPS和SSL证书
- [ ] 设置防火墙规则
- [ ] 定期备份数据库

### 性能优化
- [ ] 使用生产模式 (`FLASK_ENV=production`)
- [ ] 配置Nginx反向代理
- [ ] 设置日志轮转
- [ ] 监控系统资源

### 监控建议
- [ ] 定期检查服务状态
- [ ] 监控磁盘空间使用
- [ ] 设置SSL证书自动续期

## 📚 相关文档

- [服务器完整配置记录](服务器完整配置记录.md) - 详细部署指南
- [云服务器部署指南](云服务器部署指南.md) - 快速部署说明
- [使用指南](使用指南.md) - 功能使用说明

## 🆘 获取帮助

如果遇到问题：
1. 查看应用日志：`journalctl -u wonk-chatbot -f`
2. 检查服务状态：`systemctl status wonk-chatbot`
3. 查看相关文档
4. 在GitHub提交Issue

## 📞 联系方式

- 项目地址: https://github.com/Wilboerht/Wonk--Wilboerht-Chatbot-
- 在线体验: https://chatbot.wilboerht.cn

---

**快速命令参考：**

本地开发：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py
```

服务器部署：
```bash
systemctl status wonk-chatbot    # 查看状态
systemctl restart wonk-chatbot   # 重启服务
journalctl -u wonk-chatbot -f    # 查看日志
```

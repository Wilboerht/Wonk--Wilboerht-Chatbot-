# Windows 部署指南

本指南介绍如何在 Windows 系统上快速部署和管理 Wonk Chatbot。

## 项目概述

Wonk 是一个基于 Flask 的智能聊天机器人，具有以下特性：
- 🤖 智能对话系统，支持多种对话场景
- 💬 现代化的 Web 界面，类似 ChatGPT 的用户体验
- 📱 实时聊天功能，支持多会话管理
- 💾 SQLite 数据持久化存储，保存聊天历史
- 🎨 响应式设计，支持桌面和移动设备
- 🌐 多语言支持（中英文）
- 🔍 全文搜索功能，快速查找历史对话
- 🛠️ 完整的数据库管理工具

## 快速开始

### 1. 一键环境配置
```powershell
# 下载项目后，在项目根目录运行
powershell -ExecutionPolicy Bypass -File setup_simple.ps1
```

这个脚本会自动：
- 检查 Python 安装（需要 Python 3.8+）
- 创建虚拟环境
- 安装所有依赖
- 创建配置文件
- 设置数据目录

### 2. 启动服务

**最简单的方式（推荐）：**
```batch
# 双击启动脚本
start_chatbot.bat
```

**或者使用 PowerShell：**
```powershell
# PowerShell 启动脚本
.\start_chatbot.ps1
```

**手动启动：**
```batch
# 激活虚拟环境
.venv\Scripts\activate

# 启动应用
python app.py

# 监听所有网卡
.\run.bat --host 0.0.0.0
```

### 3. 检查状态
```batch
.\status_simple.bat
```

### 3. 访问应用

启动成功后，在浏览器中访问：
- **本地访问**：http://localhost:5000
- **局域网访问**：http://你的IP地址:5000

### 4. 停止服务

在命令行窗口按 `Ctrl + C` 或关闭命令行窗口

## 功能使用

### 聊天功能
- **发送消息**：在底部输入框输入消息，按回车或点击发送按钮
- **新对话**：点击左侧"新对话"按钮创建新的聊天会话
- **切换对话**：点击左侧历史会话列表切换到不同对话
- **删除对话**：鼠标悬停在会话上，点击垃圾桶图标删除

### 支持的对话类型
- 问候语：你好、hello、hi
- 告别语：再见、bye、拜拜
- 感谢语：谢谢、thank you
- 自我介绍：你是谁、介绍自己
- 时间查询：现在几点、时间
- 帮助信息：帮助、help、功能

### 数据库管理
```batch
# 查看聊天统计
python scripts/chat_db_manager.py stats

# 列出所有会话
python scripts/chat_db_manager.py list

# 查看特定会话
python scripts/chat_db_manager.py show <会话ID>

# 清理旧数据（30天前）
python scripts/chat_db_manager.py cleanup --days 30 --execute

# 导出聊天数据
python scripts/chat_db_manager.py export backup.json
```

## 脚本说明

### setup_simple.ps1 - 环境配置脚本
**功能：**
- 自动检测 Python 版本
- 创建虚拟环境
- 安装依赖包
- 创建配置文件

**参数：**
- `-Force`: 强制重新创建虚拟环境
- `-SkipDeps`: 跳过依赖安装
- `-Verbose`: 详细输出

**使用示例：**
```powershell
# 基本安装
powershell -ExecutionPolicy Bypass -File setup_simple.ps1

# 强制重新安装
powershell -ExecutionPolicy Bypass -File setup_simple.ps1 -Force

# 只创建环境，不安装依赖
powershell -ExecutionPolicy Bypass -File setup_simple.ps1 -SkipDeps
```

### run.bat - 启动脚本
**功能：**
- 支持开发/生产模式
- 可配置主机和端口
- 自动检查环境和依赖

**参数：**
- `--dev`: 开发模式（默认，启用热重载）
- `--prod`: 生产模式（禁用热重载）
- `--host HOST`: 指定主机地址
- `--port PORT`: 指定端口
- `--help`: 显示帮助信息

### status_simple.bat - 状态检查脚本
**功能：**
- 检查虚拟环境状态
- 验证依赖安装
- 检查配置文件
- 检查端口占用
- 测试服务健康状态

### stop.bat - 停止脚本
**功能：**
- 查找并停止相关进程
- 释放端口占用
- 显示停止状态

## 配置管理

### 环境变量配置
1. 复制 `.env.example` 为 `.env`
2. 修改关键配置：
```env
# 管理员Token（必须修改）
WONK_ADMIN_TOKEN=your-secure-admin-token-here

# 模型配置（可选）
WONK_FE_MODEL=BAAI/bge-small-zh-v1.5

# 日志级别（可选）
LOG_LEVEL=INFO
```

### 生产环境配置
1. 复制 `config.prod.yaml` 为 `config.yaml`
2. 根据需要修改配置
3. 使用生产模式启动：`.\run.bat --prod`

## 常见问题

### 1. Python 版本问题
**问题：** 提示 Python 版本过低
**解决：** 
- 安装 Python 3.8 或更高版本
- 确保安装时勾选 "Add Python to PATH"
- 重新运行 setup_simple.ps1

### 2. 权限问题
**问题：** PowerShell 执行策略限制
**解决：**
```powershell
# 临时允许执行
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 或使用参数运行
powershell -ExecutionPolicy Bypass -File setup_simple.ps1
```

### 3. 端口占用
**问题：** 端口 5000 被占用
**解决：**
- 关闭其他使用5000端口的程序
- 或修改 `app.py` 中的端口号
- 检查是否有其他 Flask 应用在运行

### 4. 依赖安装失败
**问题：** pip 安装依赖失败
**解决：**
```batch
# 手动安装依赖
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt

# 或使用国内镜像
.venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 5. 数据库锁定错误
**问题：** 出现 "database is locked" 错误
**解决：**
```batch
# 删除数据库文件重新创建
del data\database.db
python app.py
```

### 6. 聊天功能异常
**问题：** 发送消息后显示错误
**解决：**
- 检查控制台错误日志
- 确认数据库文件权限正常
- 重启应用程序

### 7. 服务无响应
**问题：** 服务启动但无法访问
**解决：**
- 检查防火墙设置
- 确认端口未被其他程序占用
- 查看控制台错误信息
- 尝试访问 http://127.0.0.1:5000

## 生产部署建议

### 1. 安全配置
- 修改默认管理员Token
- 配置CORS允许的来源
- 使用HTTPS（配置反向代理）

### 2. 性能优化
- 使用生产模式启动
- 配置适当的日志级别
- 定期清理日志文件

### 3. 监控和维护
- 定期检查服务状态
- 备份数据库文件
- 监控系统资源使用

### 4. 系统服务配置
可以将 Wonk 配置为 Windows 服务：
1. 使用 NSSM (Non-Sucking Service Manager)
2. 或使用 Windows Task Scheduler

## 故障排除

### 查看日志
- 控制台输出：启动时的实时日志
- 文件日志：`logs/wonk.log`（如果配置了文件日志）

### 重置环境
如果遇到严重问题，可以重置环境：
```powershell
# 删除虚拟环境
Remove-Item .venv -Recurse -Force

# 重新配置
powershell -ExecutionPolicy Bypass -File setup_simple.ps1 -Force
```

### 联系支持
如果问题仍然存在：
1. 收集错误信息和日志
2. 记录系统环境（Python版本、Windows版本）
3. 描述具体的操作步骤和错误现象

---

**相关文档：**
- 《数据导入指南》- 如何导入FAQ数据
- 《鉴权使用示例》- API安全配置
- 《运行与维护》- 详细的运维指南

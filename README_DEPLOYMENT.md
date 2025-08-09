# Wonk Chatbot 部署指南

## 🚀 快速开始（推荐）

### 1. 一键环境配置
```powershell
# 在项目根目录运行
powershell -ExecutionPolicy Bypass -File setup_basic.ps1
```

### 2. 启动服务
```batch
# 开发模式（默认）
.\run.bat

# 生产模式
.\run.bat --prod

# 自定义端口
.\run.bat --port 8080
```

### 3. 访问服务
- 主页：http://127.0.0.1:8000
- API文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

## 📋 可用脚本

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `setup_basic.ps1` | 环境配置 | 首次安装或重置环境 |
| `run.bat` | 启动服务 | 日常启动服务 |
| `stop.bat` | 停止服务 | 停止运行中的服务 |
| `status_simple.bat` | 状态检查 | 检查环境和服务状态 |

## 🔧 详细配置

### 环境配置脚本参数
```powershell
# 基本安装
powershell -ExecutionPolicy Bypass -File setup_basic.ps1

# 强制重新创建虚拟环境
powershell -ExecutionPolicy Bypass -File setup_basic.ps1 -Force

# 跳过依赖安装（仅创建环境）
powershell -ExecutionPolicy Bypass -File setup_basic.ps1 -SkipDeps
```

### 启动脚本参数
```batch
# 显示帮助
.\run.bat --help

# 开发模式（热重载）
.\run.bat --dev

# 生产模式（无热重载）
.\run.bat --prod

# 指定主机和端口
.\run.bat --host 0.0.0.0 --port 8080
```

## 🔐 安全配置

### 1. 修改管理员Token
编辑 `.env` 文件：
```env
WONK_ADMIN_TOKEN=your-secure-token-here
```

### 2. 受保护的接口
以下接口需要管理员Token：
- `GET /api/config` - 查看配置
- `PUT /api/config` - 修改配置
- `POST /api/ingest` - 导入数据
- `POST /api/rebuild_index` - 重建索引

### 3. 使用Token访问API
```bash
curl -H "Authorization: Bearer your-secure-token-here" \
  http://127.0.0.1:8000/api/config
```

## 📊 数据导入

### CSV/Excel 转换工具
```bash
# 预览数据
.venv\Scripts\python scripts\convert_data.py data\your_file.csv --preview

# 转换为JSONL
.venv\Scripts\python scripts\convert_data.py data\your_file.csv -o output.jsonl

# 直接导入数据库
.venv\Scripts\python scripts\convert_data.py data\your_file.xlsx
```

### 数据格式要求
- **必需列**：question, answer
- **可选列**：language, tags, source

## 🔍 状态检查

运行状态检查脚本：
```batch
.\status_simple.bat
```

检查内容：
- ✅ 虚拟环境状态
- ✅ Python依赖安装
- ✅ 配置文件存在
- ✅ 端口占用情况
- ✅ 服务健康状态

## 🛠️ 故障排除

### 常见问题

1. **Python版本问题**
   ```
   ERROR: Python 3.8+ not found
   ```
   - 安装Python 3.8+并添加到PATH

2. **权限问题**
   ```
   ExecutionPolicy限制
   ```
   - 使用 `-ExecutionPolicy Bypass` 参数

3. **端口占用**
   ```
   Port 8000 already in use
   ```
   - 运行 `.\stop.bat` 或使用其他端口

4. **依赖安装失败**
   ```
   pip install失败
   ```
   - 手动运行：`.venv\Scripts\pip install -r requirements.txt`

### 重置环境
```powershell
# 删除虚拟环境
Remove-Item .venv -Recurse -Force

# 重新配置
powershell -ExecutionPolicy Bypass -File setup_basic.ps1 -Force
```

## 🌐 生产部署

### 1. 安全检查清单
- [ ] 修改默认管理员Token
- [ ] 配置CORS允许的来源
- [ ] 使用HTTPS（配置反向代理）
- [ ] 设置防火墙规则

### 2. 性能优化
- [ ] 使用生产模式启动：`.\run.bat --prod`
- [ ] 配置适当的日志级别
- [ ] 定期备份数据库文件

### 3. 监控建议
- [ ] 定期运行状态检查
- [ ] 监控系统资源使用
- [ ] 设置日志轮转

## 📚 相关文档

- [数据转换工具使用指南](docs/数据转换工具使用指南.md)
- [鉴权使用示例](docs/鉴权使用示例.md)
- [Windows部署指南](docs/Windows部署指南.md)
- [运行与维护](docs/运行与维护.md)

## 🆘 获取帮助

如果遇到问题：
1. 查看控制台错误信息
2. 运行 `.\status_simple.bat` 检查环境
3. 查看相关文档
4. 收集错误信息和系统环境信息

---

**快速命令参考：**
```batch
# 完整工作流程
powershell -ExecutionPolicy Bypass -File setup_basic.ps1  # 配置环境
.\run.bat                                                  # 启动服务
.\status_simple.bat                                        # 检查状态
.\stop.bat                                                 # 停止服务
```

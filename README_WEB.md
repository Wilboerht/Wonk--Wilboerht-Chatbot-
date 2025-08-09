# Wonk Chatbot Web 界面

一个现代化的聊天机器人Web界面，类似ChatGPT的设计风格。

## 功能特性

- 🎨 **现代化UI设计** - 渐变背景、毛玻璃效果、响应式布局
- 💬 **实时聊天** - 流畅的对话体验，支持打字指示器
- 🤖 **智能回复** - 基于关键词的智能回复系统
- 📱 **响应式设计** - 支持桌面和移动设备
- ⚡ **快速响应** - 基于Flask的轻量级后端
- 💾 **对话历史** - 自动保存聊天记录到SQLite数据库
- 📂 **会话管理** - 创建、切换、删除多个对话会话
- 👤 **用户会话** - 基于浏览器session的用户识别
- 🔍 **历史搜索** - 可查看和恢复历史对话

## 项目结构

```text
Wonk (Wilboerht Chatbot)/
├── app.py                    # Flask主应用
├── requirements.txt          # Python依赖
├── data/
│   └── database.db          # SQLite数据库文件
├── app/
│   ├── core/
│   │   ├── chat_service.py  # 聊天服务模块
│   │   └── data_manager.py  # 数据库管理
│   └── models/
│       └── schemas.py       # 数据模型
├── templates/
│   └── index.html          # 主页模板
├── static/
│   ├── css/
│   │   └── style.css       # 样式文件
│   └── js/
│       └── app.js          # 前端JavaScript
├── scripts/
│   └── chat_db_manager.py  # 数据库管理脚本
└── README_WEB.md           # 项目说明
```

## 快速开始

### 1. 安装依赖

确保你已经激活了虚拟环境，然后安装依赖：

```bash
pip install Flask==2.3.3 Werkzeug==2.3.7 Jinja2==3.1.2
```

### 2. 启动应用

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:5000

## 使用说明

1. **开始对话** - 在底部输入框中输入消息，按回车或点击发送按钮
2. **新对话** - 点击左侧边栏的"新对话"按钮开始新的对话
3. **切换会话** - 点击左侧边栏中的历史对话来切换到不同的会话
4. **删除会话** - 鼠标悬停在会话上，点击垃圾桶图标删除会话
5. **自动保存** - 所有对话都会自动保存到数据库中
6. **语音功能** - 点击麦克风图标（功能待实现）

## 数据库管理

项目包含了一个数据库管理脚本，可以用来管理聊天数据：

```bash
# 查看所有会话
python scripts/chat_db_manager.py list

# 查看特定会话的消息
python scripts/chat_db_manager.py show <session_id>

# 显示数据库统计信息
python scripts/chat_db_manager.py stats

# 清理30天前的旧会话（预览模式）
python scripts/chat_db_manager.py cleanup --days 30

# 实际执行清理
python scripts/chat_db_manager.py cleanup --days 30 --execute

# 导出会话数据
python scripts/chat_db_manager.py export chat_backup.json
```

## 支持的对话类型

当前版本支持以下类型的对话：

- 问候语（你好、hello等）
- 告别语（再见、bye等）
- 感谢语（谢谢、thank等）
- 自我介绍（你是谁、介绍等）
- 时间查询（时间、几点等）
- 帮助信息（帮助、help、功能等）
- 通用对话（其他任何话题）

## 自定义和扩展

### 添加新的回复逻辑

在 `app.py` 的 `generate_response()` 函数中添加新的关键词匹配逻辑：

```python
elif any(word in user_message_lower for word in ['新关键词', 'new keyword']):
    return "你的自定义回复"
```

### 集成真实AI模型

替换 `generate_response()` 函数，集成OpenAI GPT、本地模型等：

```python
def generate_response(user_message):
    # 调用你的AI模型API
    response = your_ai_model.generate(user_message)
    return response
```

### 修改样式

编辑 `static/css/style.css` 文件来自定义界面样式：

- 修改颜色主题
- 调整布局
- 添加动画效果

## 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **样式**: CSS Grid, Flexbox, CSS动画
- **图标**: Font Awesome 6.0

## 浏览器支持

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## API 端点

Web应用提供了以下REST API端点：

- `POST /chat` - 发送聊天消息
- `GET /sessions` - 获取用户的会话列表
- `POST /sessions` - 创建新会话
- `DELETE /sessions/<id>` - 删除指定会话
- `GET /sessions/<id>/messages` - 获取会话的消息历史
- `GET /health` - 健康检查

## 开发计划

- [x] ~~实现对话历史保存~~ ✅ 已完成
- [x] ~~添加会话管理功能~~ ✅ 已完成
- [x] ~~创建数据库管理工具~~ ✅ 已完成
- [ ] 集成真实AI模型（OpenAI GPT、本地模型等）
- [ ] 添加语音输入/输出功能
- [ ] 添加用户认证系统
- [ ] 支持文件上传和图片对话
- [ ] 添加主题切换功能
- [ ] 实现多语言支持
- [ ] 添加对话搜索功能
- [ ] 实现对话导入/导出功能

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

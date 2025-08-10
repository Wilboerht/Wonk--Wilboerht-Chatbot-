class ChatApp {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.isTyping = false;
        this.currentSessionId = null;
        this.sessions = [];
        this.init();
    }

    init() {
        // 绑定事件监听器
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 监听输入变化以控制发送按钮状态和自动调整高度
        this.messageInput.addEventListener('input', () => {
            this.updateSendButton();
            this.autoResizeTextarea();
        });

        // 自动聚焦输入框
        this.messageInput.focus();

        // 初始化发送按钮状态
        this.updateSendButton();

        // 加载会话列表
        this.loadSessions();
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isTyping;
    }

    clearWelcomeMessage() {
        const welcomeScreen = this.chatContainer.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.remove();
        }
    }

    addWelcomeScreen() {
        const welcomeHTML = `
            <div class="welcome-screen">
                <div class="welcome-content">
                    <div class="welcome-logo">
                        <span class="welcome-logo-text">Wonk</span>
                    </div>
                    <h1 class="welcome-title">你好，我是 Wonk</h1>
                    <p class="welcome-subtitle">我可以帮你解答问题、协助思考，让我们开始对话吧</p>

                    <!-- 快速开始建议 -->
                    <div class="quick-start">
                        <div class="quick-item" onclick="sendQuickMessage('你好，介绍一下自己')">
                            <span class="quick-icon">👋</span>
                            <span class="quick-text">打个招呼</span>
                        </div>
                        <div class="quick-item" onclick="sendQuickMessage('你能帮我做什么？')">
                            <span class="quick-icon">❓</span>
                            <span class="quick-text">了解功能</span>
                        </div>
                        <div class="quick-item" onclick="sendQuickMessage('帮我写一首诗')">
                            <span class="quick-icon">✍️</span>
                            <span class="quick-text">创意写作</span>
                        </div>
                        <div class="quick-item" onclick="sendQuickMessage('解释一下人工智能')">
                            <span class="quick-icon">🤖</span>
                            <span class="quick-text">知识问答</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.chatContainer.innerHTML = welcomeHTML;
    }

    // 自动调整textarea高度
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // 添加用户消息
        this.addMessage(message, 'user');
        this.messageInput.value = '';

        // 显示打字指示器
        this.showTypingIndicator();

        try {
            // 发送消息到后端
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });

            const data = await response.json();
            
            // 隐藏打字指示器
            this.hideTypingIndicator();

            if (data.success) {
                // 更新当前会话ID
                this.currentSessionId = data.session_id;

                // 添加机器人回复
                this.addMessage(data.response, 'bot');

                // 更新会话列表
                this.loadSessions();
            } else {
                this.addMessage('抱歉，发生了错误，请稍后再试。', 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.addMessage('网络连接错误，请检查网络后重试。', 'bot');
        }
    }

    addMessage(content, type) {
        // 清除欢迎消息
        this.clearWelcomeMessage();

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '你' : 'W';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        messageBubble.textContent = content;

        messageContent.appendChild(messageBubble);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // 更新发送按钮状态
        this.updateSendButton();
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.updateSendButton();

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = 'W';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        messageBubble.textContent = '正在输入...';

        messageContent.appendChild(messageBubble);
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(messageContent);

        this.chatContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.updateSendButton();

        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    async startNewChat() {
        try {
            // 创建新会话
            const response = await fetch('/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            const data = await response.json();
            if (data.success) {
                this.currentSessionId = data.session_id;
                this.chatContainer.innerHTML = '';
                this.addWelcomeScreen();
                this.messageInput.focus();
                this.loadSessions();
            }
        } catch (error) {
            console.error('Error creating new chat:', error);
        }
    }

    async loadSessions() {
        try {
            const response = await fetch('/sessions');
            const data = await response.json();

            if (data.success) {
                this.sessions = data.sessions;
                this.updateSessionsList();
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
        }
    }

    updateSessionsList() {
        const historyContainer = document.querySelector('.chat-history');
        if (!historyContainer) return;

        historyContainer.innerHTML = '';

        this.sessions.forEach(session => {
            const sessionItem = document.createElement('div');
            sessionItem.className = `history-item ${session.id === this.currentSessionId ? 'active' : ''}`;
            sessionItem.innerHTML = `
                <i class="fas fa-message"></i>
                <span class="session-title">${session.title}</span>
                <button class="delete-session-btn" onclick="chatApp.deleteSession(${session.id}, event)">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            sessionItem.onclick = (e) => {
                if (!e.target.closest('.delete-session-btn')) {
                    this.loadSession(session.id);
                }
            };
            historyContainer.appendChild(sessionItem);
        });
    }

    async loadSession(sessionId) {
        try {
            this.currentSessionId = sessionId;

            // 获取会话消息
            const response = await fetch(`/sessions/${sessionId}/messages`);
            const data = await response.json();

            if (data.success) {
                this.chatContainer.innerHTML = '';

                // 显示历史消息
                data.messages.forEach(message => {
                    this.addMessage(message.content, message.role === 'user' ? 'user' : 'bot');
                });

                this.updateSessionsList();
            }
        } catch (error) {
            console.error('Error loading session:', error);
        }
    }

    async deleteSession(sessionId, event) {
        event.stopPropagation();

        if (!confirm('确定要删除这个对话吗？')) {
            return;
        }

        try {
            const response = await fetch(`/sessions/${sessionId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            if (data.success) {
                // 如果删除的是当前会话，清空聊天区域
                if (sessionId === this.currentSessionId) {
                    this.currentSessionId = null;
                    this.chatContainer.innerHTML = '';
                }

                this.loadSessions();
            }
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    }
}

// 全局函数
function sendMessage() {
    chatApp.sendMessage();
}

function startNewChat() {
    chatApp.startNewChat();
}

function toggleVoice() {
    // 语音功能占位符
    console.log('语音功能待实现');
}

// 初始化应用
const chatApp = new ChatApp();

// 快速开始功能
function sendQuickMessage(message) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = message;
    chatApp.updateSendButton();
    chatApp.sendMessage();
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 保持界面简洁，不自动添加欢迎消息
});

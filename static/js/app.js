class ChatApp {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.isTyping = false;
        this.currentSessionId = null;
        this.sessions = [];
        this.init();
    }

    init() {
        // 绑定事件监听器
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 自动聚焦输入框
        this.messageInput.focus();

        // 加载会话列表
        this.loadSessions();
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
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-robot"></i>';

        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        typingContent.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;

        typingDiv.appendChild(avatar);
        typingDiv.appendChild(typingContent);
        this.chatContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
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
                }
            });

            const data = await response.json();
            if (data.success) {
                this.currentSessionId = data.session_id;
                this.chatContainer.innerHTML = '';
                this.messageInput.focus();
                this.loadSessions();

                // 添加欢迎消息
                setTimeout(() => {
                    this.addMessage('你好！我是 Wonk，你的智能助手。有什么我可以帮助你的吗？', 'bot');
                }, 500);
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

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 如果没有当前会话，显示欢迎消息
    setTimeout(() => {
        if (!chatApp.currentSessionId) {
            chatApp.addMessage('你好！我是 Wonk，你的智能助手。有什么我可以帮助你的吗？', 'bot');
        }
    }, 1000);
});

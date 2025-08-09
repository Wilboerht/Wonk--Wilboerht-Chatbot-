from flask import Flask, render_template, request, jsonify, session
import json
import time
import random
import uuid
from datetime import datetime

# 导入聊天服务
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.chat_service import chat_service

app = Flask(__name__)
app.secret_key = 'wonk-chatbot-secret-key-change-in-production'  # 用于session管理

# 模拟的聊天机器人回复
SAMPLE_RESPONSES = [
    "这是一个很有趣的问题！让我想想...",
    "根据我的理解，我认为...",
    "这个话题很复杂，不过我可以为你解释一下...",
    "感谢你的提问！这让我想到了...",
    "这是一个很好的观点。从另一个角度来看...",
    "我理解你的困惑。让我为你详细说明...",
    "这确实是一个值得深入讨论的话题...",
    "基于现有的信息，我的建议是...",
]

def generate_response(user_message):
    """
    生成机器人回复的函数
    这里可以集成真正的AI模型，比如OpenAI GPT、本地模型等
    """
    # 模拟处理时间
    time.sleep(random.uniform(1, 3))
    
    # 简单的关键词回复逻辑
    user_message_lower = user_message.lower()
    
    if any(word in user_message_lower for word in ['你好', 'hello', 'hi', '您好']):
        return "你好！很高兴见到你！我是 Wonk，你的智能助手。有什么我可以帮助你的吗？"
    
    elif any(word in user_message_lower for word in ['再见', 'bye', '拜拜', '再会']):
        return "再见！希望我们的对话对你有帮助。期待下次与你交流！"
    
    elif any(word in user_message_lower for word in ['谢谢', 'thank', '感谢']):
        return "不客气！我很高兴能够帮助你。如果还有其他问题，随时可以问我！"
    
    elif any(word in user_message_lower for word in ['你是谁', '介绍', 'who are you']):
        return "我是 Wonk，一个智能聊天机器人。我可以回答问题、提供建议、进行对话。我的目标是为用户提供有用和有趣的交流体验！"
    
    elif any(word in user_message_lower for word in ['天气', 'weather']):
        return "抱歉，我目前还无法获取实时天气信息。不过你可以查看天气应用或网站来获取最新的天气预报！"
    
    elif any(word in user_message_lower for word in ['时间', 'time', '几点']):
        current_time = time.strftime("%Y年%m月%d日 %H:%M:%S")
        return f"现在的时间是：{current_time}"
    
    elif any(word in user_message_lower for word in ['帮助', 'help', '功能']):
        return """我可以帮助你：
• 回答各种问题
• 进行日常对话
• 提供建议和想法
• 解释概念和知识点
• 协助解决问题

你可以问我任何你感兴趣的话题！"""
    
    else:
        # 随机选择一个通用回复
        base_response = random.choice(SAMPLE_RESPONSES)
        return f"{base_response}\n\n关于「{user_message}」这个话题，我觉得这很值得深入探讨。你能告诉我更多相关的背景信息吗？"

@app.route('/')
def index():
    """主页路由"""
    return render_template('index.html')

def get_user_id():
    """获取或创建用户ID"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']


@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天消息的API端点"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')

        if not user_message:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            })

        # 获取用户ID
        user_id = get_user_id()

        # 使用聊天服务处理消息
        chat_response = chat_service.send_message(
            message=user_message,
            session_id=session_id,
            user_id=user_id
        )

        return jsonify({
            'success': chat_response.success,
            'response': chat_response.response,
            'session_id': chat_response.session_id,
            'message_id': chat_response.message_id,
            'timestamp': chat_response.timestamp.isoformat() if chat_response.timestamp else None,
            'error': chat_response.error
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500

@app.route('/sessions', methods=['GET'])
def get_sessions():
    """获取用户的聊天会话列表"""
    try:
        user_id = get_user_id()
        sessions = chat_service.get_sessions_list(user_id)
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        print(f"Error in get_sessions: {e}")
        return jsonify({
            'success': False,
            'error': '获取会话列表失败'
        }), 500


@app.route('/sessions', methods=['POST'])
def create_session():
    """创建新的聊天会话"""
    try:
        data = request.get_json() or {}
        title = data.get('title')
        user_id = get_user_id()

        session_id = chat_service.create_session(title, user_id)
        return jsonify({
            'success': True,
            'session_id': session_id
        })
    except Exception as e:
        print(f"Error in create_session: {e}")
        return jsonify({
            'success': False,
            'error': '创建会话失败'
        }), 500


@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除聊天会话"""
    try:
        success = chat_service.delete_session(session_id)
        return jsonify({
            'success': success
        })
    except Exception as e:
        print(f"Error in delete_session: {e}")
        return jsonify({
            'success': False,
            'error': '删除会话失败'
        }), 500


@app.route('/sessions/<int:session_id>/messages', methods=['GET'])
def get_session_messages(session_id):
    """获取会话的消息历史"""
    try:
        messages = chat_service.get_session_history(session_id)
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        print(f"Error in get_session_messages: {e}")
        return jsonify({
            'success': False,
            'error': '获取消息历史失败'
        }), 500


@app.route('/health')
def health():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    import os

    # 获取环境变量
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'

    print("🤖 Wonk Chatbot 正在启动...")
    if debug:
        print("📱 访问 http://localhost:5000 开始聊天")
    else:
        print(f"🌐 生产模式启动，端口: {port}")

    app.run(host='0.0.0.0', port=port, debug=debug)

"""
聊天服务模块
处理聊天逻辑、会话管理和消息存储
"""

import time
import random
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.data_manager import (
    create_chat_session, get_chat_sessions, get_chat_session,
    add_chat_message, get_chat_messages, delete_chat_session,
    get_chat_session_by_latest_message, init_db
)
from app.models.schemas import ChatSession, ChatMessage, ChatRequest, ChatResponse
from app.utils.logger import logger


class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        # 确保数据库已初始化
        init_db()
        
        # 模拟的聊天机器人回复
        self.sample_responses = [
            "这是一个很有趣的问题！让我想想...",
            "根据我的理解，我认为...",
            "这个话题很复杂，不过我可以为你解释一下...",
            "感谢你的提问！这让我想到了...",
            "这是一个很好的观点。从另一个角度来看...",
            "我理解你的困惑。让我为你详细说明...",
            "这确实是一个值得深入讨论的话题...",
            "基于现有的信息，我的建议是...",
        ]
    
    def generate_response(self, user_message: str) -> str:
        """
        生成机器人回复的函数
        这里可以集成真正的AI模型，比如OpenAI GPT、本地模型等
        """
        # 模拟处理时间
        time.sleep(random.uniform(0.5, 2.0))
        
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
            base_response = random.choice(self.sample_responses)
            return f"{base_response}\n\n关于「{user_message}」这个话题，我觉得这很值得深入探讨。你能告诉我更多相关的背景信息吗？"
    
    def create_session(self, title: str = None, user_id: str = None) -> int:
        """创建新的聊天会话"""
        if not title:
            title = f"新对话 - {datetime.now().strftime('%m月%d日 %H:%M')}"
        
        session_id = create_chat_session(title, user_id)
        logger.info(f"Created new chat session: {session_id}")
        return session_id
    
    def get_or_create_session(self, session_id: Optional[int] = None, user_id: str = None) -> int:
        """获取或创建聊天会话"""
        if session_id:
            # 验证会话是否存在
            session = get_chat_session(session_id)
            if session:
                return session_id
        
        # 尝试获取最近的会话
        recent_session = get_chat_session_by_latest_message(user_id)
        if recent_session:
            return recent_session['id']
        
        # 创建新会话
        return self.create_session(user_id=user_id)
    
    def send_message(self, message: str, session_id: Optional[int] = None, user_id: str = None) -> ChatResponse:
        """发送消息并获取回复"""
        try:
            # 获取或创建会话
            actual_session_id = self.get_or_create_session(session_id, user_id)
            
            # 保存用户消息
            user_message_id = add_chat_message(actual_session_id, 'user', message)
            
            # 生成机器人回复
            bot_response = self.generate_response(message)
            
            # 保存机器人回复
            bot_message_id = add_chat_message(actual_session_id, 'assistant', bot_response)
            
            logger.info(f"Chat exchange in session {actual_session_id}: user_msg={user_message_id}, bot_msg={bot_message_id}")
            
            return ChatResponse(
                success=True,
                response=bot_response,
                session_id=actual_session_id,
                message_id=bot_message_id,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in send_message: {e}")
            return ChatResponse(
                success=False,
                response=None,
                session_id=session_id or 0,
                error=str(e)
            )
    
    def get_session_history(self, session_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """获取会话历史"""
        try:
            messages = get_chat_messages(session_id, limit)
            return [
                {
                    'id': msg['id'],
                    'role': msg['role'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp']
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []
    
    def get_sessions_list(self, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """获取会话列表"""
        try:
            sessions = get_chat_sessions(user_id, limit)
            return [
                {
                    'id': session['id'],
                    'title': session['title'],
                    'created_at': session['created_at'],
                    'updated_at': session['updated_at']
                }
                for session in sessions
            ]
        except Exception as e:
            logger.error(f"Error getting sessions list: {e}")
            return []
    
    def delete_session(self, session_id: int) -> bool:
        """删除会话"""
        try:
            deleted_count = delete_chat_session(session_id)
            logger.info(f"Deleted chat session {session_id}, affected rows: {deleted_count}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False


# 全局聊天服务实例
chat_service = ChatService()

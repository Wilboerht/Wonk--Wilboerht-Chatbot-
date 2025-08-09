#!/usr/bin/env python3
"""
聊天数据库管理脚本
用于管理聊天会话和消息数据
"""

import sys
import os
import argparse
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.data_manager import (
    init_db, get_conn, get_chat_sessions, get_chat_messages,
    delete_chat_session, create_chat_session, add_chat_message
)


def list_sessions(user_id=None, limit=50):
    """列出聊天会话"""
    sessions = get_chat_sessions(user_id, limit)
    
    print(f"\n📋 聊天会话列表 (共 {len(sessions)} 个):")
    print("-" * 80)
    print(f"{'ID':<5} {'标题':<30} {'用户ID':<20} {'创建时间':<20} {'更新时间':<20}")
    print("-" * 80)
    
    for session in sessions:
        print(f"{session['id']:<5} {session['title'][:29]:<30} {session['user_id'] or 'N/A':<20} "
              f"{session['created_at'][:19]:<20} {session['updated_at'][:19]:<20}")


def show_session_messages(session_id, limit=100):
    """显示会话消息"""
    messages = get_chat_messages(session_id, limit)
    
    print(f"\n💬 会话 {session_id} 的消息 (共 {len(messages)} 条):")
    print("-" * 80)
    
    for msg in messages:
        role_icon = "👤" if msg['role'] == 'user' else "🤖"
        timestamp = msg['timestamp'][:19] if msg['timestamp'] else 'N/A'
        print(f"\n{role_icon} [{msg['role'].upper()}] {timestamp}")
        print(f"   {msg['content']}")


def cleanup_old_sessions(days=30, dry_run=True):
    """清理旧的会话"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with get_conn() as conn:
        cur = conn.cursor()
        
        # 查找旧会话
        cur.execute(
            "SELECT id, title, updated_at FROM chat_sessions WHERE updated_at < ?",
            (cutoff_date.isoformat(),)
        )
        old_sessions = cur.fetchall()
        
        print(f"\n🧹 发现 {len(old_sessions)} 个超过 {days} 天的会话:")
        
        if not old_sessions:
            print("   没有需要清理的会话")
            return
        
        for session in old_sessions:
            print(f"   - ID: {session['id']}, 标题: {session['title']}, 最后更新: {session['updated_at']}")
        
        if dry_run:
            print(f"\n⚠️  这是预览模式，使用 --execute 参数来实际删除")
            return
        
        # 实际删除
        deleted_count = 0
        for session in old_sessions:
            try:
                delete_chat_session(session['id'])
                deleted_count += 1
                print(f"   ✅ 已删除会话 {session['id']}")
            except Exception as e:
                print(f"   ❌ 删除会话 {session['id']} 失败: {e}")
        
        print(f"\n✅ 成功删除 {deleted_count} 个会话")


def export_sessions(output_file, user_id=None):
    """导出会话数据"""
    import json
    
    sessions = get_chat_sessions(user_id, limit=1000)
    export_data = []
    
    for session in sessions:
        messages = get_chat_messages(session['id'], limit=1000)
        session_data = {
            'id': session['id'],
            'title': session['title'],
            'user_id': session['user_id'],
            'created_at': session['created_at'],
            'updated_at': session['updated_at'],
            'messages': [
                {
                    'id': msg['id'],
                    'role': msg['role'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp']
                }
                for msg in messages
            ]
        }
        export_data.append(session_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已导出 {len(export_data)} 个会话到 {output_file}")


def show_stats():
    """显示数据库统计信息"""
    with get_conn() as conn:
        cur = conn.cursor()
        
        # 会话统计
        cur.execute("SELECT COUNT(*) FROM chat_sessions")
        session_count = cur.fetchone()[0]
        
        # 消息统计
        cur.execute("SELECT COUNT(*) FROM chat_messages")
        message_count = cur.fetchone()[0]
        
        # 用户统计
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM chat_sessions WHERE user_id IS NOT NULL")
        user_count = cur.fetchone()[0]
        
        # 最近活动
        cur.execute("SELECT MAX(updated_at) FROM chat_sessions")
        last_activity = cur.fetchone()[0]
        
        print(f"\n📊 数据库统计信息:")
        print("-" * 40)
        print(f"总会话数:     {session_count}")
        print(f"总消息数:     {message_count}")
        print(f"活跃用户数:   {user_count}")
        print(f"最后活动:     {last_activity or 'N/A'}")


def main():
    parser = argparse.ArgumentParser(description='聊天数据库管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出会话
    list_parser = subparsers.add_parser('list', help='列出聊天会话')
    list_parser.add_argument('--user-id', help='指定用户ID')
    list_parser.add_argument('--limit', type=int, default=50, help='限制结果数量')
    
    # 显示会话消息
    show_parser = subparsers.add_parser('show', help='显示会话消息')
    show_parser.add_argument('session_id', type=int, help='会话ID')
    show_parser.add_argument('--limit', type=int, default=100, help='限制消息数量')
    
    # 清理旧会话
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧会话')
    cleanup_parser.add_argument('--days', type=int, default=30, help='清理多少天前的会话')
    cleanup_parser.add_argument('--execute', action='store_true', help='实际执行删除操作')
    
    # 导出数据
    export_parser = subparsers.add_parser('export', help='导出会话数据')
    export_parser.add_argument('output_file', help='输出文件路径')
    export_parser.add_argument('--user-id', help='指定用户ID')
    
    # 统计信息
    subparsers.add_parser('stats', help='显示数据库统计信息')
    
    # 初始化数据库
    subparsers.add_parser('init', help='初始化数据库')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 确保数据库已初始化
    init_db()
    
    if args.command == 'list':
        list_sessions(args.user_id, args.limit)
    elif args.command == 'show':
        show_session_messages(args.session_id, args.limit)
    elif args.command == 'cleanup':
        cleanup_old_sessions(args.days, not args.execute)
    elif args.command == 'export':
        export_sessions(args.output_file, args.user_id)
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'init':
        print("✅ 数据库已初始化")


if __name__ == '__main__':
    main()

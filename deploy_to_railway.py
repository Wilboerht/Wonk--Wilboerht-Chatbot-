#!/usr/bin/env python3
"""
Wonk Chatbot Railway部署脚本
自动化部署到Railway平台
"""

import os
import subprocess
import sys
import json

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e.stderr}")
        return None

def check_requirements():
    """检查部署要求"""
    print("🔍 检查部署要求...")
    
    # 检查git
    if not run_command("git --version", "检查Git"):
        print("请安装Git: https://git-scm.com/")
        return False
    
    # 检查是否在git仓库中
    if not os.path.exists('.git'):
        print("❌ 当前目录不是Git仓库")
        print("请先运行: git init && git add . && git commit -m 'Initial commit'")
        return False
    
    # 检查必要文件
    required_files = ['app.py', 'requirements.txt', 'templates/index.html']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return False
    
    print("✅ 所有要求检查通过")
    return True

def setup_railway():
    """设置Railway CLI"""
    print("🚀 设置Railway...")
    
    # 检查Railway CLI是否已安装
    if not run_command("railway --version", "检查Railway CLI"):
        print("📦 安装Railway CLI...")
        
        # Windows
        if os.name == 'nt':
            print("请手动安装Railway CLI:")
            print("1. 访问: https://railway.app/cli")
            print("2. 下载并安装Railway CLI")
            print("3. 重新运行此脚本")
            return False
        
        # macOS/Linux
        install_cmd = "curl -fsSL https://railway.app/install.sh | sh"
        if not run_command(install_cmd, "安装Railway CLI"):
            return False
    
    # 登录Railway
    print("🔐 请在浏览器中登录Railway...")
    if not run_command("railway login", "登录Railway"):
        return False
    
    return True

def deploy_to_railway():
    """部署到Railway"""
    print("🚀 开始部署到Railway...")
    
    # 初始化Railway项目
    if not run_command("railway init", "初始化Railway项目"):
        return False
    
    # 设置环境变量
    env_vars = {
        "FLASK_ENV": "production",
        "PYTHONUNBUFFERED": "1"
    }
    
    for key, value in env_vars.items():
        cmd = f'railway variables set {key}="{value}"'
        run_command(cmd, f"设置环境变量 {key}")
    
    # 部署
    if not run_command("railway up", "部署应用"):
        return False
    
    # 获取部署URL
    url_output = run_command("railway status", "获取部署状态")
    if url_output:
        print("🎉 部署成功！")
        print("🌐 你的聊天机器人现在可以通过以下网址访问：")
        # 解析URL（简化版本）
        print("   请在Railway控制台查看具体网址")
        print("   或运行: railway open")
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 Wonk Chatbot Railway部署工具")
    print("=" * 50)
    print()
    
    # 检查要求
    if not check_requirements():
        sys.exit(1)
    
    # 设置Railway
    if not setup_railway():
        print("\n❌ Railway设置失败")
        print("请手动完成以下步骤：")
        print("1. 安装Railway CLI: https://railway.app/cli")
        print("2. 运行: railway login")
        print("3. 重新运行此脚本")
        sys.exit(1)
    
    # 部署
    if deploy_to_railway():
        print("\n🎉 部署完成！")
        print("\n📋 后续步骤：")
        print("1. 运行 'railway open' 打开你的应用")
        print("2. 在Railway控制台查看日志和监控")
        print("3. 可以绑定自定义域名")
        print("\n💡 提示：")
        print("- 代码更新后，再次运行 'railway up' 即可重新部署")
        print("- 使用 'railway logs' 查看应用日志")
    else:
        print("\n❌ 部署失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()

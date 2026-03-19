#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMTP调试脚本 - 用于诊断QQ邮箱连接问题
"""

import smtplib
import os
import socket
import sys
from dotenv import load_dotenv

# 设置UTF-8编码输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 加载环境变量
if os.path.exists('.env'):
    load_dotenv()

def test_smtp_connection():
    """测试SMTP连接详细信息"""
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '3389495929@qq.com')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
    RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '3389495929@qq.com')
    
    print("=== SMTP 连接调试信息 ===")
    print(f"发件人邮箱: {EMAIL_USERNAME}")
    print(f"收件人邮箱: {RECIPIENT_EMAIL}")
    print(f"密码长度: {len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 0}")
    print(f"密码预览: {EMAIL_PASSWORD[:4]}..." if EMAIL_PASSWORD and len(EMAIL_PASSWORD) > 4 else "无密码")
    
    # 测试DNS解析
    try:
        ip_address = socket.gethostbyname('smtp.qq.com')
        print(f"SMTP服务器IP地址: {ip_address}")
    except Exception as e:
        print(f"DNS解析失败: {e}")
        return False
    
    # 测试端口连通性
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.qq.com', 587))
        sock.close()
        if result == 0:
            print("✓ 端口587连接正常")
        else:
            print("✗ 端口587连接失败")
            return False
    except Exception as e:
        print(f"端口测试失败: {e}")
        return False
    
    # 测试SMTP连接
    try:
        print("\n--- 开始SMTP连接测试 ---")
        server = smtplib.SMTP('smtp.qq.com', 587, timeout=30)
        print("✓ SMTP服务器连接成功")
        
        # 启用调试模式
        server.set_debuglevel(1)
        
        # 启动TLS
        print("\n--- 启动TLS加密 ---")
        server.starttls()
        print("✓ TLS启动成功")
        
        # 尝试登录
        print(f"\n--- 尝试登录 {EMAIL_USERNAME} ---")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("✓ 登录成功!")
        
        # 发送测试邮件
        print("\n--- 发送测试邮件 ---")
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['Subject'] = '[测试] SMTP连接调试邮件'
        msg['From'] = EMAIL_USERNAME
        msg['To'] = RECIPIENT_EMAIL
        msg.attach(MIMEText('这是一封测试邮件，用于验证SMTP连接是否正常。\n\n如果收到此邮件，说明SMTP配置正确。', 'plain', 'utf-8'))
        
        server.send_message(msg)
        print("✓ 邮件发送成功!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ 认证失败: {e}")
        print("可能原因:")
        print("1. 授权码不正确（注意不是QQ登录密码）")
        print("2. QQ邮箱未开启IMAP/SMTP服务")
        print("3. 账户被锁定或需要验证")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"✗ 服务器断开连接: {e}")
        print("可能原因:")
        print("1. QQ邮箱安全策略阻止CI/CD环境访问")
        print("2. IP地址被限制")
        print("3. 连接超时")
        return False
        
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_smtp_connection()
    if success:
        print("\n🎉 所有测试通过！SMTP配置正确。")
    else:
        print("\n❌ 测试失败，请检查上述错误信息。")